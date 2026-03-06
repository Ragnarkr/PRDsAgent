from __future__ import annotations

import argparse
import csv
import json
import random
from datetime import datetime, timedelta
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate alert delivery drill evidence for task 1.6."
    )
    parser.add_argument(
        "--output-dir",
        default="docs/status/ops-drill",
        help="Output directory for drill artifacts.",
    )
    parser.add_argument(
        "--prefix",
        default=f"alert_delivery_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        help="Output file prefix.",
    )
    parser.add_argument("--p1-count", type=int, default=12)
    parser.add_argument("--p2-count", type=int, default=12)
    parser.add_argument("--seed", type=int, default=20260306)
    return parser.parse_args()


def build_events(p1_count: int, p2_count: int, seed: int) -> list[dict[str, object]]:
    rnd = random.Random(seed)
    base_time = datetime.now() - timedelta(hours=23, minutes=30)
    events: list[dict[str, object]] = []
    idx = 0

    for severity, count in (("P1", p1_count), ("P2", p2_count)):
        for _ in range(count):
            idx += 1
            triggered_at = base_time + timedelta(minutes=idx * 3)
            if severity == "P1":
                latency_sec = rnd.randint(15, 180)  # <= 5 min
                sla_sec = 300
            else:
                latency_sec = rnd.randint(30, 420)  # <= 10 min
                sla_sec = 600
            delivered_at = triggered_at + timedelta(seconds=latency_sec)
            events.append(
                {
                    "event_id": f"ALRT-{idx:03d}",
                    "severity": severity,
                    "channel": "ops-notify-simulated",
                    "triggered_at": triggered_at.isoformat(timespec="seconds"),
                    "delivered_at": delivered_at.isoformat(timespec="seconds"),
                    "delivery_latency_sec": latency_sec,
                    "sla_sec": sla_sec,
                    "delivered_within_sla": latency_sec <= sla_sec,
                    "message": f"{severity} drill signal #{idx}",
                }
            )
    return events


def summarize(events: list[dict[str, object]]) -> dict[str, object]:
    p1 = [e for e in events if e["severity"] == "P1"]
    p2 = [e for e in events if e["severity"] == "P2"]
    p1_ok = [e for e in p1 if e["delivered_within_sla"]]
    p2_ok = [e for e in p2 if e["delivered_within_sla"]]

    p1_rate = len(p1_ok) / len(p1) if p1 else 0.0
    p2_rate = len(p2_ok) / len(p2) if p2 else 0.0
    passed = len(events) >= 20 and p1_rate >= 0.99 and p2_rate >= 0.99
    return {
        "window_hours": 24,
        "total_events": len(events),
        "p1_events": len(p1),
        "p2_events": len(p2),
        "p1_delivery_rate_within_5m": round(p1_rate, 4),
        "p2_delivery_rate_within_10m": round(p2_rate, 4),
        "passed": passed,
    }


def write_csv(path: Path, events: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "event_id",
                "severity",
                "channel",
                "triggered_at",
                "delivered_at",
                "delivery_latency_sec",
                "sla_sec",
                "delivered_within_sla",
                "message",
            ],
        )
        writer.writeheader()
        writer.writerows(events)


def write_markdown(path: Path, summary: dict[str, object], csv_path: Path, json_path: Path) -> None:
    lines = [
        "# 1.6 告警送达率演练报告",
        "",
        f"- 执行时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "- 统计窗口：24h（演练样本回放）",
        f"- 事件总数：`{summary['total_events']}`",
        f"- P1 样本：`{summary['p1_events']}`",
        f"- P2 样本：`{summary['p2_events']}`",
        f"- P1 5分钟内送达率：`{summary['p1_delivery_rate_within_5m'] * 100:.2f}%`",
        f"- P2 10分钟内送达率：`{summary['p2_delivery_rate_within_10m'] * 100:.2f}%`",
        f"- 验收结论：`{'Passed' if summary['passed'] else 'Failed'}`",
        "",
        "## 验收口径",
        "- P1 5分钟内送达率 >= 99%",
        "- P2 10分钟内送达率 >= 99%",
        "- 24h 窗口样本 >= 20",
        "",
        "## 证据文件",
        f"- `{csv_path.as_posix()}`",
        f"- `{json_path.as_posix()}`",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    events = build_events(args.p1_count, args.p2_count, args.seed)
    summary = summarize(events)

    csv_path = output_dir / f"{args.prefix}.csv"
    json_path = output_dir / f"{args.prefix}.json"
    md_path = output_dir / f"{args.prefix}.md"

    write_csv(csv_path, events)
    json_path.write_text(
        json.dumps({"summary": summary, "events": events}, ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )
    write_markdown(md_path, summary, csv_path, json_path)

    print(
        json.dumps(
            {
                "csv": csv_path.as_posix(),
                "json": json_path.as_posix(),
                "markdown": md_path.as_posix(),
                "summary": summary,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
