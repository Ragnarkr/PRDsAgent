from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from math import ceil, inf
from pathlib import Path
from typing import Iterable, Literal

RetryMode = Literal["all_attempts", "latest_attempt"]


@dataclass(slots=True)
class RequestSample:
    request_id: str
    status_code: int
    latency_ms: float
    timeout: bool = False
    attempt: int = 1


@dataclass(slots=True)
class MetricPolicy:
    retry_mode: RetryMode = "latest_attempt"
    count_4xx_as_success: bool = False


@dataclass(slots=True)
class GateThresholds:
    p95_ms: float = 6000.0
    success_rate: float = 0.99
    error_5xx_rate: float = 0.005
    timeout_rate: float = 0.005


@dataclass(slots=True)
class RoundMetrics:
    total_requests: int
    success_requests: int
    error_5xx_requests: int
    timeout_requests: int
    p95_ms: float | None

    @property
    def success_rate(self) -> float:
        return _safe_ratio(self.success_requests, self.total_requests)

    @property
    def error_5xx_rate(self) -> float:
        return _safe_ratio(self.error_5xx_requests, self.total_requests)

    @property
    def timeout_rate(self) -> float:
        return _safe_ratio(self.timeout_requests, self.total_requests)

    def to_dict(self) -> dict[str, float | int | None]:
        return {
            "total_requests": self.total_requests,
            "success_requests": self.success_requests,
            "error_5xx_requests": self.error_5xx_requests,
            "timeout_requests": self.timeout_requests,
            "p95_ms": self.p95_ms,
            "success_rate": self.success_rate,
            "error_5xx_rate": self.error_5xx_rate,
            "timeout_rate": self.timeout_rate,
        }


@dataclass(slots=True)
class GateSummary:
    p95_ms: float
    success_rate: float
    error_5xx_rate: float
    timeout_rate: float

    def is_passing(self, thresholds: GateThresholds | None = None) -> bool:
        limits = thresholds or GateThresholds()
        return (
            self.p95_ms <= limits.p95_ms
            and self.success_rate >= limits.success_rate
            and self.error_5xx_rate <= limits.error_5xx_rate
            and self.timeout_rate <= limits.timeout_rate
        )

    def to_dict(self) -> dict[str, float]:
        return {
            "p95_ms": self.p95_ms,
            "success_rate": self.success_rate,
            "error_5xx_rate": self.error_5xx_rate,
            "timeout_rate": self.timeout_rate,
        }


def compute_round_metrics(
    samples: Iterable[RequestSample],
    policy: MetricPolicy | None = None,
) -> RoundMetrics:
    config = policy or MetricPolicy()
    normalized = _apply_retry_mode(list(samples), config.retry_mode)

    success_requests = 0
    error_5xx_requests = 0
    timeout_requests = 0
    success_latencies: list[float] = []

    for sample in normalized:
        if sample.timeout:
            timeout_requests += 1
        if 500 <= sample.status_code <= 599:
            error_5xx_requests += 1

        is_success = _is_success(sample.status_code, config.count_4xx_as_success) and not sample.timeout
        if is_success:
            success_requests += 1
            success_latencies.append(sample.latency_ms)

    p95_ms = _percentile(success_latencies, 95.0) if success_latencies else None
    return RoundMetrics(
        total_requests=len(normalized),
        success_requests=success_requests,
        error_5xx_requests=error_5xx_requests,
        timeout_requests=timeout_requests,
        p95_ms=p95_ms,
    )


def compute_gate_summary(rounds: Iterable[RoundMetrics]) -> GateSummary:
    round_list = list(rounds)
    if not round_list:
        raise ValueError("At least one round metric is required.")

    p95_values = [metric.p95_ms for metric in round_list if metric.p95_ms is not None]
    return GateSummary(
        p95_ms=max(p95_values) if p95_values else inf,
        success_rate=min(metric.success_rate for metric in round_list),
        error_5xx_rate=max(metric.error_5xx_rate for metric in round_list),
        timeout_rate=max(metric.timeout_rate for metric in round_list),
    )


def load_samples_jsonl(path: Path) -> list[RequestSample]:
    samples: list[RequestSample] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, raw in enumerate(handle, start=1):
            payload = raw.strip()
            if not payload:
                continue
            item = json.loads(payload)
            try:
                samples.append(
                    RequestSample(
                        request_id=str(item["request_id"]),
                        status_code=int(item["status_code"]),
                        latency_ms=float(item["latency_ms"]),
                        timeout=bool(item.get("timeout", False)),
                        attempt=int(item.get("attempt", 1)),
                    )
                )
            except KeyError as exc:
                raise ValueError(
                    f"Missing required key {exc} at {path}:{line_no}"
                ) from exc
    return samples


def build_report(
    paths: list[Path],
    policy: MetricPolicy | None = None,
    thresholds: GateThresholds | None = None,
) -> dict[str, object]:
    config = policy or MetricPolicy()
    limits = thresholds or GateThresholds()

    rounds: list[RoundMetrics] = []
    for path in paths:
        rounds.append(compute_round_metrics(load_samples_jsonl(path), config))
    summary = compute_gate_summary(rounds)

    return {
        "policy": asdict(config),
        "thresholds": asdict(limits),
        "rounds": [round_metric.to_dict() for round_metric in rounds],
        "summary": summary.to_dict(),
        "gate_passed": summary.is_passing(limits),
    }


def _apply_retry_mode(samples: list[RequestSample], mode: RetryMode) -> list[RequestSample]:
    if mode == "all_attempts":
        return samples

    latest_by_request: dict[str, tuple[int, int, RequestSample]] = {}
    for index, sample in enumerate(samples):
        current = latest_by_request.get(sample.request_id)
        rank = (sample.attempt, index)
        if current is None or rank >= current[:2]:
            latest_by_request[sample.request_id] = (sample.attempt, index, sample)

    ordered = sorted(latest_by_request.values(), key=lambda item: item[1])
    return [entry[2] for entry in ordered]


def _is_success(status_code: int, count_4xx_as_success: bool) -> bool:
    if 200 <= status_code <= 299:
        return True
    if count_4xx_as_success and 400 <= status_code <= 499:
        return True
    return False


def _safe_ratio(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return numerator / denominator


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        raise ValueError("Cannot compute percentile of an empty list.")
    ordered = sorted(values)
    rank = max(1, ceil((percentile / 100.0) * len(ordered)))
    return ordered[rank - 1]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute Gate-M1 baseline metrics from request JSONL files."
    )
    parser.add_argument(
        "files",
        nargs="+",
        help="Round files in JSONL format.",
    )
    parser.add_argument(
        "--retry-mode",
        choices=("all_attempts", "latest_attempt"),
        default="latest_attempt",
        help="Whether retries are counted as independent requests.",
    )
    parser.add_argument(
        "--count-4xx-as-success",
        action="store_true",
        help="Treat 4xx responses as successful requests for success-rate and P95 calculations.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    report = build_report(
        paths=[Path(path) for path in args.files],
        policy=MetricPolicy(
            retry_mode=args.retry_mode,
            count_4xx_as_success=args.count_4xx_as_success,
        ),
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
