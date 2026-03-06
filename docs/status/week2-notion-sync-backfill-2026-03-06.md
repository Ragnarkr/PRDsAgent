# Week2 Notion Sync Backfill Package (2026-03-06)

## 1. Scope And Contract
- Target database: `PRDsAgent项目`
- Scope: Week2 tasks `1.1~1.8`
- Unified status dictionary: `Not Started | In Progress | Completed | Blocked`
- Required page title format: `M1-W2-<task_id>-<任务名>-<状态>`

## 2. Locked Baseline
| task_id | 任务名 | status | Notion page title |
|---|---|---|---|
| 1.1 | 数据授权与脱敏前置闸门 | Completed | M1-W2-1.1-数据授权与脱敏前置闸门-Completed |
| 1.2 | 规则引擎 v1 完整化 | Completed | M1-W2-1.2-规则引擎 v1 完整化-Completed |
| 1.3 | 离线评测集 v1 与标注规范 | Completed | M1-W2-1.3-离线评测集 v1 与标注规范-Completed |
| 1.4 | 性能测量脚本与基线报告 | Completed | M1-W2-1.4-性能测量脚本与基线报告-Completed |
| 1.5 | PoC 技术审查与口径冻结 | Completed | M1-W2-1.5-PoC 技术审查与口径冻结-Completed |
| 1.6 | 运维与合规闭环任务 | In Progress | M1-W2-1.6-运维与合规闭环任务-In Progress |
| 1.7 | 发布基线与回滚准入矩阵 | In Progress | M1-W2-1.7-发布基线与回滚准入矩阵-In Progress |
| 1.8 | 周中风险复盘与阻塞治理 | In Progress | M1-W2-1.8-周中风险复盘与阻塞治理-In Progress |

## 3. Task Payload For Notion Body
| task_id | deliverables | acceptance result | evidence links | blocker + ETA |
|---|---|---|---|---|
| 1.1 | 授权登记、闸门检查、脱敏规则、抽检报告 | Passed（未授权样本=0；脱敏覆盖率=100%） | `docs/status/1.1-data-authorization-register.csv`; `docs/status/1.1-access-gate-check.md`; `docs/status/1.1-desensitization-rules-v1.md`; `docs/status/1.1-desensitization-sampling-report.md` | None |
| 1.2 | 规则实现、JSON 报告格式、接口清单 v0.1 | Passed（规则测试通过） | `src/prds_agent/rules/engine.py`; `tests/test_rule_engine.py`; `docs/status/week2-deliverables-2026-03-05.md` | None |
| 1.3 | dataset/manifest/hash/标注手册 | Passed（120样本；三格式各40；抽检一致率95.83%；hash可校验） | `docs/status/1.3-test-cases-completion-plan.md`; `docs/status/1.3-test-execution-results.md`; `docs/status/1.3-sample-distribution-report.md`; `docs/status/1.3-double-review-consistency-report.md`; `docs/status/dataset-m1-v1-manifest.hash` | None |
| 1.4 | 压测脚本/三轮原始结果/指标计算说明 | Passed（真实staging三轮通过） | `docs/status/1.4-performance-baseline-plan.md`; `docs/status/1.4-performance-real-staging-execution-2026-03-06.md`; `docs/status/perf-test-data/staging_real_20260306_2_gate_report.json`; `docs/status/perf-test-data/staging_real_20260306_2_5xx_distribution.md` | None |
| 1.5 | 技术审查记录/口径冻结确认单 | Passed（四方签字完成） | `docs/status/1.5-technical-integration-plan.md`; `docs/status/tech-review-and-freeze.md` | None |
| 1.6 | 告警链路验证/回滚演练/合规检查 | Pending | `docs/status/1.6-1.7-monitoring-alert-plan.md`; `docs/status/devops-baseline-alert-plan.md` | 前置(1.4)已满足，待告警验收与回滚演练；ETA 2026-04-03 |
| 1.7 | 准入矩阵/回滚阈值/RTO-RPO | Pending | `docs/status/1.6-1.7-monitoring-alert-plan.md`; `docs/status/release-rollback-gate.md` | 依赖 1.4 与 1.6；ETA 2026-04-04 |
| 1.8 | 风险台账/阻塞升级记录/周收口矩阵 | Pending | `docs/status/1.8-pm-summary-plan.md`; `docs/status/m1-week2-week3-execution-board.md`; `docs/status/week2-closure-matrix-2026-03-06.md` | 依赖 1.3~1.7 全部可验收；ETA 2026-04-05 |

## 4. Notion Write Attempt Log
- Attempt #1, 2026-03-06: `list_mcp_resources(server=notion)`
  - Result: `MCP startup failed: handshaking with MCP server failed ... https://mcp.notion.com/mcp`
- Attempt #2, 2026-03-06: `list_mcp_resource_templates(server=notion)`
  - Result: same handshake failure.

## 5. Recovery Rule
- Current sync status: `Blocked` (integration channel).
- Recovery SLA: backfill to Notion within 30 minutes after Notion MCP channel is restored.
- Conflict handling: if local and Notion conflict at the same timestamp, PM latest backfill wins.
