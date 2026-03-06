from __future__ import annotations

import argparse
import json
import random
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from prds_agent.metrics.baseline import build_report  # noqa: E402


@dataclass(frozen=True)
class RoundProfile:
    avg_latency_ms: float
    latency_jitter_ms: float
    timeout_rate: float
    error_5xx_rate: float


ROUND_PROFILES = (
    RoundProfile(avg_latency_ms=2450.0, latency_jitter_ms=650.0, timeout_rate=0.002, error_5xx_rate=0.004),
    RoundProfile(avg_latency_ms=2680.0, latency_jitter_ms=720.0, timeout_rate=0.003, error_5xx_rate=0.005),
    RoundProfile(avg_latency_ms=2380.0, latency_jitter_ms=620.0, timeout_rate=0.001, error_5xx_rate=0.003),
)


def _bounded_latency(value: float) -> float:
    return max(200.0, min(value, 5900.0))


def _gen_round_records(round_idx: int, n_requests: int, seed: int) -> list[dict[str, object]]:
    rnd = random.Random(seed + round_idx * 101)
    profile = ROUND_PROFILES[(round_idx - 1) % len(ROUND_PROFILES)]
    records: list[dict[str, object]] = []

    for i in range(1, n_requests + 1):
        request_id = f"r{round_idx:02d}-{i:04d}"
        timeout = rnd.random() < profile.timeout_rate
        is_5xx = (not timeout) and (rnd.random() < profile.error_5xx_rate)
        latency = _bounded_latency(rnd.gauss(profile.avg_latency_ms, profile.latency_jitter_ms))
        status_code = 500 if is_5xx else 200

        records.append(
            {
                "request_id": request_id,
                "status_code": status_code,
                "latency_ms": round(latency, 3),
                "timeout": timeout,
                "attempt": 1,
            }
        )
    return records


def _write_jsonl(path: Path, records: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def _format_pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def _write_markdown_report(
    report_path: Path,
    round_files: list[Path],
    summary: dict[str, object],
    requests_per_round: int,
    warmup_requests: int,
    concurrency: int,
    seed: int,
) -> None:
    rounds = summary["rounds"]
    gate_summary = summary["summary"]
    lines = [
        "# 1.4 压测基线启动报告（staging-dry-run）",
        "",
        f"- 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "- 模式：`dry-run`（用于先完成口径、脚本与产物链路验证）",
        f"- 每轮请求：`{requests_per_round}`（预热 `{warmup_requests}`）",
        f"- 并发：`{concurrency}`",
        "- 时长口径：`10分钟模型`（此报告为离线模拟，不代表真实环境耗时）",
        f"- 随机种子：`{seed}`",
        "",
        "## 原始结果文件",
    ]
    for f in round_files:
        lines.append(f"- `{f.as_posix()}`")

    lines.extend(
        [
            "",
            "## 分轮指标",
            "| Round | total | success_rate | 5xx_rate | timeout_rate | p95_ms |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )

    for idx, item in enumerate(rounds, start=1):
        lines.append(
            f"| {idx} | {item['total_requests']} | {_format_pct(item['success_rate'])} | "
            f"{_format_pct(item['error_5xx_rate'])} | {_format_pct(item['timeout_rate'])} | "
            f"{item['p95_ms']:.3f} |"
        )

    lines.extend(
        [
            "",
            "## 最差值 Gate 汇总",
            f"- p95_ms(max): `{gate_summary['p95_ms']:.3f}`（阈值 <= 6000）",
            f"- success_rate(min): `{_format_pct(gate_summary['success_rate'])}`（阈值 >= 99.00%）",
            f"- error_5xx_rate(max): `{_format_pct(gate_summary['error_5xx_rate'])}`（阈值 <= 0.50%）",
            f"- timeout_rate(max): `{_format_pct(gate_summary['timeout_rate'])}`（阈值 <= 0.50%）",
            f"- gate_passed: `{summary['gate_passed']}`",
            "",
            "## 结论",
            "- 已完成三轮原始结果 + 最差值计算的端到端流程打通。",
            "- 当前结果仅作为 1.4 启动证据；正式验收仍需真实 staging 三轮压测与资源水位记录。",
        ]
    )

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate 3-round baseline JSONL data and compute Gate summary."
    )
    parser.add_argument(
        "--output-dir",
        default="docs/status/perf-test-data",
        help="Directory to store round JSONL and reports.",
    )
    parser.add_argument(
        "--rounds",
        type=int,
        default=3,
        help="Number of rounds to generate.",
    )
    parser.add_argument(
        "--requests-per-round",
        type=int,
        default=500,
        help="Requests per round (excluding warmup).",
    )
    parser.add_argument(
        "--warmup-requests",
        type=int,
        default=50,
        help="Warmup requests count metadata.",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=20,
        help="Concurrency metadata.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=20260306,
        help="Random seed for deterministic data generation.",
    )
    parser.add_argument(
        "--prefix",
        default="staging_dryrun",
        help="Prefix used in generated file names.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    round_files: list[Path] = []
    for round_idx in range(1, args.rounds + 1):
        file_path = output_dir / f"{args.prefix}_round{round_idx}.jsonl"
        records = _gen_round_records(
            round_idx=round_idx,
            n_requests=args.requests_per_round,
            seed=args.seed,
        )
        _write_jsonl(file_path, records)
        round_files.append(file_path)

    report = build_report(paths=round_files)
    json_report_path = output_dir / f"{args.prefix}_gate_report.json"
    json_report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    markdown_report_path = output_dir / f"{args.prefix}_gate_report.md"
    _write_markdown_report(
        report_path=markdown_report_path,
        round_files=round_files,
        summary=report,
        requests_per_round=args.requests_per_round,
        warmup_requests=args.warmup_requests,
        concurrency=args.concurrency,
        seed=args.seed,
    )

    print(
        json.dumps(
            {
                "round_files": [path.as_posix() for path in round_files],
                "json_report": json_report_path.as_posix(),
                "markdown_report": markdown_report_path.as_posix(),
                "gate_passed": report["gate_passed"],
                "summary": report["summary"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
