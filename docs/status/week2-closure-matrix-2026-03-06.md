# Week2 收口矩阵（2026-03-06）

## 1. 状态基线
- 状态字典：`Not Started | In Progress | Completed | Blocked`
- 本次基线口径：`1.1~1.8=Completed`

## 2. Week2 任务矩阵（1.1~1.8）

| 任务ID | 状态 | 验收结论 | 证据链接 | 风险余项 |
|---|---|---|---|---|
| 1.1 | Completed | 通过（未授权样本=0；脱敏覆盖率=100%） | `docs/status/1.1-data-authorization-register.csv`；`docs/status/1.1-access-gate-check.md`；`docs/status/1.1-desensitization-rules-v1.md`；`docs/status/1.1-desensitization-sampling-report.md` | 无 |
| 1.2 | Completed | 通过（规则引擎v1交付且测试通过） | `src/prds_agent/rules/engine.py`；`tests/test_rule_engine.py`；`docs/status/week2-deliverables-2026-03-05.md` | 无 |
| 1.3 | Completed | 通过（样本总数=120；三格式各40；双人抽检一致率=95.83%；manifest/hash可校验） | `docs/status/1.3-test-cases-completion-plan.md`；`docs/status/1.3-test-execution-results.md`；`docs/status/1.3-sample-distribution-report.md`；`docs/status/1.3-double-review-consistency-report.md`；`docs/status/dataset-m1-v1-manifest.hash` | 无 |
| 1.4 | Completed | 通过（真实staging三轮：p95=543.316ms；成功率=100%；5xx=0%；超时=0%） | `docs/status/1.4-performance-baseline-plan.md`；`docs/status/1.4-performance-real-staging-execution-2026-03-06.md`；`docs/status/perf-test-data/staging_real_20260306_2_gate_report.json`；`docs/status/perf-test-data/staging_real_20260306_2_5xx_distribution.md` | 无 |
| 1.5 | Completed | 通过（技术评审签字完成，指标口径冻结v1.0） | `docs/status/1.5-technical-integration-plan.md`；`docs/status/tech-review-and-freeze.md` | 无 |
| 1.6 | Completed | 通过（告警送达率与回滚演练已闭环） | `docs/status/1.6-1.7-monitoring-alert-plan.md`；`docs/status/1.6-ops-compliance-closure-2026-03-06.md`；`docs/status/ops-drill/ops_alert_delivery_20260306.md`；`docs/status/ops-drill/ops_rollback_drill_20260306.md` | 无 |
| 1.7 | Completed | 通过（准入矩阵与回滚阈值已冻结并联签） | `docs/status/1.6-1.7-monitoring-alert-plan.md`；`docs/status/release-rollback-gate.md` | 无 |
| 1.8 | Completed | 通过（风险复盘与阻塞治理完成，Notion回填已留痕） | `docs/status/1.8-pm-summary-plan.md`；`docs/status/m1-week2-week3-execution-board.md`；`docs/status/week2-notion-sync-backfill-2026-03-06.md` | 无 |

## 3. 当前收口结论
- Week2 已完成：`1.1`、`1.2`、`1.3`、`1.4`、`1.5`、`1.6`、`1.7`、`1.8`
- Week2 进行中：无
- Week2 可宣告全量完成，后续进入 Week3 复测与 Gate 评审阶段。

## 4. Notion Sync Status
- Sync target: `PRDsAgent项目` database, Week2 task pages `1.1~1.8`.
- Current result: `Completed`（MCP 已恢复并完成回填）。
- Backfill package: `docs/status/week2-notion-sync-backfill-2026-03-06.md`.
- 回填页面：
  - `https://www.notion.so/31b96011ac3e818ca57ec3c2c24d9a24`
  - `https://www.notion.so/31b96011ac3e81a7bcd8ebfdae1e8389`
