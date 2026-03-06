# Week2 收口矩阵（2026-03-06）

## 1. 状态基线
- 状态字典：`Not Started | In Progress | Completed | Blocked`
- 本次基线口径：`1.1=Completed`、`1.2=Completed`、`1.3=Completed`、`1.4~1.8=In Progress`

## 2. Week2 任务矩阵（1.1~1.8）

| 任务ID | 状态 | 验收结论 | 证据链接 | 风险余项 |
|---|---|---|---|---|
| 1.1 | Completed | 通过（未授权样本=0；脱敏覆盖率=100%） | `docs/status/1.1-data-authorization-register.csv`；`docs/status/1.1-access-gate-check.md`；`docs/status/1.1-desensitization-rules-v1.md`；`docs/status/1.1-desensitization-sampling-report.md` | 无 |
| 1.2 | Completed | 通过（规则引擎v1交付且测试通过） | `src/prds_agent/rules/engine.py`；`tests/test_rule_engine.py`；`docs/status/week2-deliverables-2026-03-05.md` | 无 |
| 1.3 | Completed | 通过（样本总数=120；三格式各40；双人抽检一致率=95.83%；manifest/hash可校验） | `docs/status/1.3-test-cases-completion-plan.md`；`docs/status/1.3-test-execution-results.md`；`docs/status/1.3-sample-distribution-report.md`；`docs/status/1.3-double-review-consistency-report.md`；`docs/status/dataset-m1-v1-manifest.hash` | 无 |
| 1.4 | In Progress | 待验收（dry-run三轮已完成，真实staging三轮未完成） | `docs/status/1.4-performance-baseline-plan.md`；`docs/status/1.4-performance-dryrun-execution-2026-03-06.md`；`docs/status/perf-test-data/staging_dryrun_20260306_gate_report.md` | staging环境与请求画像未完全就绪；dry-run显示5xx率0.60%高于阈值 |
| 1.5 | In Progress | 待验收（待1.3/1.4首版后冻结口径） | `docs/status/1.5-technical-integration-plan.md`；`docs/status/subagent-architecture-design-review-2026-03-05.md` | 依赖前置输出未齐套 |
| 1.6 | In Progress | 待验收（告警链路与回滚演练未闭环） | `docs/status/1.6-1.7-monitoring-alert-plan.md`；`docs/status/devops-baseline-alert-plan.md` | 依赖1.4性能基线首版 |
| 1.7 | In Progress | 待验收（准入矩阵未完成联签） | `docs/status/1.6-1.7-monitoring-alert-plan.md`；`docs/status/release-rollback-gate.md` | 依赖1.4与1.6产出 |
| 1.8 | In Progress | 待验收（汇总收口依赖1.3~1.7） | `docs/status/1.8-pm-summary-plan.md`；`docs/status/m1-week2-week3-execution-board.md` | 上游任务未全部闭环 |

## 3. 当前收口结论
- Week2 已完成：`1.1`、`1.2`、`1.3`
- Week2 进行中：`1.4`、`1.5`、`1.6`、`1.7`、`1.8`
- 当前不可宣告 Week2 全量完成，需继续按依赖链推进并完成证据闭环。

## 4. Notion Sync Status
- Sync target: `PRDsAgent项目` database, Week2 task pages `1.1~1.8`.
- Current result: `Blocked` due to Notion MCP handshake failure.
- Backfill package: `docs/status/week2-notion-sync-backfill-2026-03-06.md`.
- Recovery rule: MCP恢复后 30 minutes 内完成 Notion 回填；同时间戳冲突以 PM 最后回填记录为准。
