from __future__ import annotations

import unittest

from prds_agent.metrics import (
    MetricPolicy,
    RequestSample,
    compute_gate_summary,
    compute_round_metrics,
)


class PerfBaselineTest(unittest.TestCase):
    def test_retry_mode_latest_attempt_keeps_last_attempt_only(self) -> None:
        samples = [
            RequestSample(request_id="req-1", status_code=500, latency_ms=180.0, attempt=1),
            RequestSample(request_id="req-1", status_code=200, latency_ms=95.0, attempt=2),
            RequestSample(request_id="req-2", status_code=200, latency_ms=110.0, attempt=1),
        ]

        metrics = compute_round_metrics(samples, MetricPolicy(retry_mode="latest_attempt"))

        self.assertEqual(metrics.total_requests, 2)
        self.assertEqual(metrics.success_requests, 2)
        self.assertEqual(metrics.error_5xx_requests, 0)
        self.assertAlmostEqual(metrics.success_rate, 1.0)

    def test_retry_mode_all_attempts_counts_every_retry(self) -> None:
        samples = [
            RequestSample(request_id="req-1", status_code=500, latency_ms=180.0, attempt=1),
            RequestSample(request_id="req-1", status_code=200, latency_ms=95.0, attempt=2),
            RequestSample(request_id="req-2", status_code=200, latency_ms=110.0, attempt=1),
        ]

        metrics = compute_round_metrics(samples, MetricPolicy(retry_mode="all_attempts"))

        self.assertEqual(metrics.total_requests, 3)
        self.assertEqual(metrics.success_requests, 2)
        self.assertEqual(metrics.error_5xx_requests, 1)
        self.assertAlmostEqual(metrics.success_rate, 2 / 3)

    def test_4xx_success_boundary_is_configurable(self) -> None:
        samples = [RequestSample(request_id="req-1", status_code=404, latency_ms=70.0)]

        metrics_default = compute_round_metrics(samples, MetricPolicy(count_4xx_as_success=False))
        metrics_with_4xx = compute_round_metrics(samples, MetricPolicy(count_4xx_as_success=True))

        self.assertEqual(metrics_default.success_requests, 0)
        self.assertEqual(metrics_with_4xx.success_requests, 1)

    def test_p95_and_gate_summary_use_worst_case(self) -> None:
        round_a = compute_round_metrics(
            [
                RequestSample(request_id=f"a-{i}", status_code=200, latency_ms=float(ms))
                for i, ms in enumerate([100, 110, 120, 130, 1000], start=1)
            ]
        )
        round_b = compute_round_metrics(
            [
                RequestSample(request_id="b-1", status_code=200, latency_ms=200.0),
                RequestSample(request_id="b-2", status_code=500, latency_ms=210.0),
                RequestSample(request_id="b-3", status_code=200, latency_ms=220.0, timeout=True),
            ]
        )

        summary = compute_gate_summary([round_a, round_b])

        self.assertEqual(round_a.p95_ms, 1000.0)
        self.assertEqual(summary.p95_ms, 1000.0)
        self.assertAlmostEqual(summary.success_rate, min(round_a.success_rate, round_b.success_rate))
        self.assertAlmostEqual(summary.error_5xx_rate, max(round_a.error_5xx_rate, round_b.error_5xx_rate))
        self.assertAlmostEqual(summary.timeout_rate, max(round_a.timeout_rate, round_b.timeout_rate))


if __name__ == "__main__":
    unittest.main()
