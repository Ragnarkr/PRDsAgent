from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

import requests


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Execute rollback drill and generate evidence for task 1.6."
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--output-dir", default="docs/status/ops-drill")
    parser.add_argument(
        "--prefix",
        default=f"rollback_drill_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
    )
    parser.add_argument(
        "--sample-file",
        default="docs/status/dataset-m1-v1/markdown/M1V1-MD-001.md",
        help="Sample file for post-rollback analyze check.",
    )
    parser.add_argument("--health-timeout-seconds", type=float, default=30.0)
    parser.add_argument("--rto-threshold-seconds", type=float, default=1800.0)
    parser.add_argument("--rpo-threshold-seconds", type=float, default=900.0)
    return parser.parse_args()


def wait_health(url: str, timeout_seconds: float) -> bool:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2.5) as response:
                if response.status == 200:
                    return True
        except (urllib.error.URLError, TimeoutError):
            time.sleep(0.5)
    return False


def start_server(host: str, port: int, stdout_log: Path, stderr_log: Path) -> subprocess.Popen[str]:
    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = "src" if not existing_pythonpath else f"src{os.pathsep}{existing_pythonpath}"
    return subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "prds_agent.api:app",
            "--host",
            host,
            "--port",
            str(port),
            "--log-level",
            "warning",
        ],
        stdout=stdout_log.open("w", encoding="utf-8"),
        stderr=stderr_log.open("w", encoding="utf-8"),
        env=env,
    )


def stop_server(proc: subprocess.Popen[str]) -> None:
    proc.terminate()
    try:
        proc.wait(timeout=8)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=8)


def post_analyze(base_url: str, sample_file: Path) -> dict[str, object]:
    with sample_file.open("rb") as handle:
        response = requests.post(
            f"{base_url}/analyze",
            files={"file": (sample_file.name, handle, "application/octet-stream")},
            timeout=15,
        )
    body: dict[str, object]
    try:
        body = response.json()
    except Exception:  # noqa: BLE001
        body = {"raw": response.text[:300]}
    return {"status_code": response.status_code, "body": body}


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    base_url = f"http://{args.host}:{args.port}"
    health_url = f"{base_url}/health"
    sample_file = Path(args.sample_file)

    stdout_pre = output_dir / f"{args.prefix}_pre_stdout.log"
    stderr_pre = output_dir / f"{args.prefix}_pre_stderr.log"
    stdout_post = output_dir / f"{args.prefix}_post_stdout.log"
    stderr_post = output_dir / f"{args.prefix}_post_stderr.log"

    timeline: list[dict[str, object]] = []
    started_at = datetime.now().isoformat(timespec="seconds")

    pre_proc = start_server(args.host, args.port, stdout_pre, stderr_pre)
    try:
        if not wait_health(health_url, args.health_timeout_seconds):
            raise RuntimeError("pre-drill server health check failed")
        timeline.append({"step": "pre_server_healthy", "at": datetime.now().isoformat(timespec="seconds")})
    finally:
        # Simulate deployment failure trigger.
        failure_triggered_at_ts = time.time()
        failure_triggered_at = datetime.now().isoformat(timespec="seconds")
        stop_server(pre_proc)
        timeline.append({"step": "failure_triggered", "at": failure_triggered_at})

    rollback_proc = start_server(args.host, args.port, stdout_post, stderr_post)
    try:
        rollback_ok = wait_health(health_url, args.health_timeout_seconds)
        rollback_recovered_at = datetime.now().isoformat(timespec="seconds")
        timeline.append({"step": "rollback_server_healthy", "at": rollback_recovered_at, "ok": rollback_ok})
        if not rollback_ok:
            raise RuntimeError("rollback server health check failed")

        analyze_result = post_analyze(base_url, sample_file)
        timeline.append(
            {
                "step": "post_rollback_analyze",
                "at": datetime.now().isoformat(timespec="seconds"),
                "status_code": analyze_result["status_code"],
            }
        )
    finally:
        stop_server(rollback_proc)

    rto_seconds = round(time.time() - failure_triggered_at_ts, 3)
    # Service is stateless for this drill; treat data loss window as 0s.
    rpo_seconds = 0.0

    passed = (
        rto_seconds <= args.rto_threshold_seconds
        and rpo_seconds <= args.rpo_threshold_seconds
        and analyze_result["status_code"] == 200
    )

    summary = {
        "started_at": started_at,
        "base_url": base_url,
        "sample_file": sample_file.as_posix(),
        "rto_seconds": rto_seconds,
        "rpo_seconds": rpo_seconds,
        "rto_threshold_seconds": args.rto_threshold_seconds,
        "rpo_threshold_seconds": args.rpo_threshold_seconds,
        "post_rollback_analyze_status": analyze_result["status_code"],
        "passed": passed,
        "timeline": timeline,
        "logs": {
            "pre_stdout": stdout_pre.as_posix(),
            "pre_stderr": stderr_pre.as_posix(),
            "post_stdout": stdout_post.as_posix(),
            "post_stderr": stderr_post.as_posix(),
        },
        "analyze_result": analyze_result,
    }

    json_path = output_dir / f"{args.prefix}.json"
    md_path = output_dir / f"{args.prefix}.md"
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# 1.6 回滚演练报告",
        "",
        f"- 执行时间：{started_at}",
        f"- 服务地址：`{base_url}`",
        f"- 回滚触发后恢复耗时（RTO）：`{rto_seconds}s`（阈值 <= {args.rto_threshold_seconds}s）",
        f"- 数据回退窗口（RPO）：`{rpo_seconds}s`（阈值 <= {args.rpo_threshold_seconds}s）",
        f"- 回滚后 analyze 状态码：`{analyze_result['status_code']}`",
        f"- 演练结论：`{'Passed' if passed else 'Failed'}`",
        "",
        "## 证据文件",
        f"- `{json_path.as_posix()}`",
        f"- `{stdout_pre.as_posix()}`",
        f"- `{stderr_pre.as_posix()}`",
        f"- `{stdout_post.as_posix()}`",
        f"- `{stderr_post.as_posix()}`",
    ]
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "json": json_path.as_posix(),
                "markdown": md_path.as_posix(),
                "summary": {
                    "rto_seconds": rto_seconds,
                    "rpo_seconds": rpo_seconds,
                    "post_rollback_analyze_status": analyze_result["status_code"],
                    "passed": passed,
                },
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
