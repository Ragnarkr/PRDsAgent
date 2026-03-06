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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Start local staging API, run real perf rounds, then stop server."
    )
    parser.add_argument("--base-url", default="http://127.0.0.1:8080")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--dataset-root", default="docs/status/dataset-m1-v1")
    parser.add_argument("--output-dir", default="docs/status/perf-test-data")
    parser.add_argument("--prefix", default=f"staging_real_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--requests-per-round", type=int, default=500)
    parser.add_argument("--warmup-requests", type=int, default=50)
    parser.add_argument("--concurrency", type=int, default=20)
    parser.add_argument("--timeout-seconds", type=float, default=30.0)
    parser.add_argument("--seed", type=int, default=20260306)
    parser.add_argument("--health-timeout-seconds", type=float, default=30.0)
    return parser.parse_args()


def wait_health(health_url: str, timeout_seconds: float) -> None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(health_url, timeout=2.5) as response:
                if response.status == 200:
                    return
        except (urllib.error.URLError, TimeoutError):
            time.sleep(0.5)
    raise TimeoutError(f"health check timeout: {health_url}")


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    stdout_log = output_dir / f"{args.prefix}_api_stdout.log"
    stderr_log = output_dir / f"{args.prefix}_api_stderr.log"

    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = "src" if not existing_pythonpath else f"src{os.pathsep}{existing_pythonpath}"

    with stdout_log.open("w", encoding="utf-8") as stdout_handle, stderr_log.open(
        "w", encoding="utf-8"
    ) as stderr_handle:
        server = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "prds_agent.api:app",
                "--host",
                args.host,
                "--port",
                str(args.port),
                "--log-level",
                "warning",
            ],
            stdout=stdout_handle,
            stderr=stderr_handle,
            env=env,
        )

        result: dict[str, object] = {}
        try:
            wait_health(f"{args.base_url.rstrip('/')}/health", args.health_timeout_seconds)
            run = subprocess.run(
                [
                    sys.executable,
                    "scripts/run_perf_staging_rounds.py",
                    "--base-url",
                    args.base_url,
                    "--dataset-root",
                    args.dataset_root,
                    "--output-dir",
                    args.output_dir,
                    "--prefix",
                    args.prefix,
                    "--rounds",
                    str(args.rounds),
                    "--requests-per-round",
                    str(args.requests_per_round),
                    "--warmup-requests",
                    str(args.warmup_requests),
                    "--concurrency",
                    str(args.concurrency),
                    "--timeout-seconds",
                    str(args.timeout_seconds),
                    "--seed",
                    str(args.seed),
                ],
                capture_output=True,
                text=True,
                env=env,
                check=False,
            )
            if run.returncode != 0:
                raise RuntimeError(
                    f"perf runner failed ({run.returncode}): {run.stderr.strip()}"
                )
            result = json.loads(run.stdout)
            result["runner_stdout"] = run.stdout
            result["runner_stderr"] = run.stderr
        finally:
            server.terminate()
            try:
                server.wait(timeout=8)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait(timeout=8)

    summary = {
        "base_url": args.base_url,
        "prefix": args.prefix,
        "api_stdout_log": stdout_log.as_posix(),
        "api_stderr_log": stderr_log.as_posix(),
        "perf_result": result,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
