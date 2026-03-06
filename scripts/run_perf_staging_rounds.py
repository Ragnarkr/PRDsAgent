from __future__ import annotations

import argparse
import asyncio
import json
import random
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

import aiohttp

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from prds_agent.metrics.baseline import build_report  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run real staging performance rounds and output Gate + 5xx distribution reports."
    )
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:8080",
        help="Base URL of staging API.",
    )
    parser.add_argument(
        "--dataset-root",
        default="docs/status/dataset-m1-v1",
        help="Dataset root containing markdown/txt/docx folders.",
    )
    parser.add_argument(
        "--output-dir",
        default="docs/status/perf-test-data",
        help="Directory for output files.",
    )
    parser.add_argument(
        "--prefix",
        default=f"staging_real_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        help="Output file prefix.",
    )
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--requests-per-round", type=int, default=500)
    parser.add_argument("--warmup-requests", type=int, default=50)
    parser.add_argument("--concurrency", type=int, default=20)
    parser.add_argument("--timeout-seconds", type=float, default=30.0)
    parser.add_argument("--seed", type=int, default=20260306)
    return parser.parse_args()


def load_dataset_files(dataset_root: Path) -> list[Path]:
    files: list[Path] = []
    for folder, pattern in (
        ("markdown", "*.md"),
        ("txt", "*.txt"),
        ("docx", "*.docx"),
    ):
        files.extend(sorted((dataset_root / folder).glob(pattern)))
    if not files:
        raise FileNotFoundError(f"No files found under {dataset_root.as_posix()}")
    return files


def parse_error_from_body(status: int, body: str) -> tuple[str, str]:
    if not body:
        return ("empty_response", "")
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return ("non_json_error", body[:200].replace("\n", " "))

    if status >= 500:
        if isinstance(payload, dict):
            message = str(payload.get("message", ""))
            details = str(payload.get("details", ""))
            code = str(payload.get("code", ""))
            detail = " | ".join(filter(None, [code, message, details]))[:300]
            return ("server_error_json", detail)
    return ("http_error_json", str(payload)[:200])


async def send_request(
    session: aiohttp.ClientSession,
    semaphore: asyncio.Semaphore,
    endpoint: str,
    file_path: Path,
    request_id: str,
    timeout_seconds: float,
) -> dict[str, Any]:
    async with semaphore:
        started = time.perf_counter()
        record: dict[str, Any] = {
            "request_id": request_id,
            "status_code": 0,
            "latency_ms": 0.0,
            "timeout": False,
            "attempt": 1,
            "file_path": file_path.as_posix(),
            "file_ext": file_path.suffix.lower(),
            "error_kind": "",
            "error_detail": "",
        }
        try:
            content = file_path.read_bytes()
            form = aiohttp.FormData()
            form.add_field(
                "file",
                content,
                filename=file_path.name,
                content_type="application/octet-stream",
            )
            timeout = aiohttp.ClientTimeout(total=timeout_seconds)
            async with session.post(endpoint, data=form, timeout=timeout) as response:
                body = await response.text()
                record["status_code"] = int(response.status)
                if response.status >= 500:
                    kind, detail = parse_error_from_body(response.status, body)
                    record["error_kind"] = kind
                    record["error_detail"] = detail
        except asyncio.TimeoutError:
            record["status_code"] = 504
            record["timeout"] = True
            record["error_kind"] = "timeout"
            record["error_detail"] = "request timed out"
        except aiohttp.ClientError as exc:
            record["status_code"] = 599
            record["error_kind"] = "network_error"
            record["error_detail"] = str(exc)[:300]
        except Exception as exc:  # noqa: BLE001
            record["status_code"] = 598
            record["error_kind"] = "client_exception"
            record["error_detail"] = str(exc)[:300]
        finally:
            record["latency_ms"] = round((time.perf_counter() - started) * 1000, 3)
        return record


async def run_round(
    round_idx: int,
    files: list[Path],
    endpoint: str,
    requests_per_round: int,
    warmup_requests: int,
    concurrency: int,
    timeout_seconds: float,
    seed: int,
) -> list[dict[str, Any]]:
    rng = random.Random(seed + round_idx * 997)
    semaphore = asyncio.Semaphore(concurrency)
    connector = aiohttp.TCPConnector(limit=concurrency * 2)

    async with aiohttp.ClientSession(connector=connector) as session:
        warmup_tasks = []
        for i in range(1, warmup_requests + 1):
            file_path = rng.choice(files)
            warmup_tasks.append(
                send_request(
                    session=session,
                    semaphore=semaphore,
                    endpoint=endpoint,
                    file_path=file_path,
                    request_id=f"warmup-r{round_idx:02d}-{i:03d}",
                    timeout_seconds=timeout_seconds,
                )
            )
        if warmup_tasks:
            await asyncio.gather(*warmup_tasks)

        tasks = []
        for i in range(1, requests_per_round + 1):
            file_path = rng.choice(files)
            tasks.append(
                send_request(
                    session=session,
                    semaphore=semaphore,
                    endpoint=endpoint,
                    file_path=file_path,
                    request_id=f"r{round_idx:02d}-{i:04d}",
                    timeout_seconds=timeout_seconds,
                )
            )
        records = await asyncio.gather(*tasks)
    return records


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in records:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def build_5xx_distribution(
    all_round_records: list[list[dict[str, Any]]],
) -> dict[str, Any]:
    by_status = Counter()
    by_round = Counter()
    by_ext = Counter()
    by_kind = Counter()
    by_detail = Counter()
    total = 0

    for round_idx, records in enumerate(all_round_records, start=1):
        for row in records:
            code = int(row["status_code"])
            if 500 <= code <= 599:
                total += 1
                by_status[str(code)] += 1
                by_round[f"round_{round_idx}"] += 1
                by_ext[str(row.get("file_ext", ""))] += 1
                by_kind[str(row.get("error_kind", ""))] += 1
                detail = str(row.get("error_detail", "")).strip()
                if detail:
                    by_detail[detail] += 1

    return {
        "total_5xx": total,
        "by_status_code": dict(by_status),
        "by_round": dict(by_round),
        "by_file_ext": dict(by_ext),
        "by_error_kind": dict(by_kind),
        "top_error_details": [
            {"detail": detail, "count": count}
            for detail, count in by_detail.most_common(10)
        ],
    }


def pct(numerator: float, denominator: float) -> str:
    if denominator == 0:
        return "0.00%"
    return f"{(numerator / denominator) * 100:.2f}%"


def write_distribution_markdown(
    path: Path,
    distribution: dict[str, Any],
    round_files: list[Path],
    report: dict[str, Any],
) -> None:
    total_requests = 0
    for round_item in report["rounds"]:
        total_requests += int(round_item["total_requests"])

    lines = [
        "# 1.4 真实 staging 5xx 错误分布分析",
        "",
        f"- 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- 原始结果文件：{', '.join(f'`{p.as_posix()}`' for p in round_files)}",
        f"- 总请求数：`{total_requests}`",
        f"- 5xx 总数：`{distribution['total_5xx']}`",
        f"- 5xx 占比：`{pct(distribution['total_5xx'], total_requests)}`",
        "",
        "## 按状态码分布",
    ]

    if distribution["by_status_code"]:
        for code, count in sorted(distribution["by_status_code"].items()):
            lines.append(f"- `{code}`: `{count}`")
    else:
        lines.append("- 无 5xx")

    lines.extend(["", "## 按轮次分布"])
    if distribution["by_round"]:
        for round_key, count in sorted(distribution["by_round"].items()):
            lines.append(f"- `{round_key}`: `{count}`")
    else:
        lines.append("- 无 5xx")

    lines.extend(["", "## 按文件类型分布"])
    if distribution["by_file_ext"]:
        for ext, count in sorted(distribution["by_file_ext"].items()):
            lines.append(f"- `{ext}`: `{count}`")
    else:
        lines.append("- 无 5xx")

    lines.extend(["", "## 错误类型与细节（Top）"])
    if distribution["by_error_kind"]:
        for kind, count in sorted(distribution["by_error_kind"].items()):
            lines.append(f"- `{kind}`: `{count}`")
    else:
        lines.append("- 无 5xx")

    if distribution["top_error_details"]:
        for item in distribution["top_error_details"]:
            lines.append(f"- `{item['count']}`: {item['detail']}")
    else:
        lines.append("- 无可用错误详情")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


async def main_async(args: argparse.Namespace) -> dict[str, Any]:
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    dataset_root = Path(args.dataset_root)
    files = load_dataset_files(dataset_root)
    endpoint = f"{args.base_url.rstrip('/')}/analyze"

    all_round_records: list[list[dict[str, Any]]] = []
    round_files: list[Path] = []

    for round_idx in range(1, args.rounds + 1):
        records = await run_round(
            round_idx=round_idx,
            files=files,
            endpoint=endpoint,
            requests_per_round=args.requests_per_round,
            warmup_requests=args.warmup_requests,
            concurrency=args.concurrency,
            timeout_seconds=args.timeout_seconds,
            seed=args.seed,
        )
        out_path = output_dir / f"{args.prefix}_round{round_idx}.jsonl"
        write_jsonl(out_path, records)
        round_files.append(out_path)
        all_round_records.append(records)

    report = build_report(paths=round_files)
    report_json_path = output_dir / f"{args.prefix}_gate_report.json"
    report_json_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    distribution = build_5xx_distribution(all_round_records)
    distribution_json_path = output_dir / f"{args.prefix}_5xx_distribution.json"
    distribution_json_path.write_text(
        json.dumps(distribution, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    distribution_md_path = output_dir / f"{args.prefix}_5xx_distribution.md"
    write_distribution_markdown(
        path=distribution_md_path,
        distribution=distribution,
        round_files=round_files,
        report=report,
    )

    return {
        "round_files": [p.as_posix() for p in round_files],
        "gate_report_json": report_json_path.as_posix(),
        "distribution_json": distribution_json_path.as_posix(),
        "distribution_md": distribution_md_path.as_posix(),
        "gate_passed": report["gate_passed"],
        "gate_summary": report["summary"],
        "distribution_summary": distribution,
    }


def main() -> int:
    args = parse_args()
    result = asyncio.run(main_async(args))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
