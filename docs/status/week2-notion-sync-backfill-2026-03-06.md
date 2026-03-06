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
| 1.3 | 离线评测集 v1 与标注规范 | In Progress | M1-W2-1.3-离线评测集 v1 与标注规范-In Progress |
| 1.4 | 性能测量脚本与基线报告 | In Progress | M1-W2-1.4-性能测量脚本与基线报告-In Progress |
| 1.5 | PoC 技术审查与口径冻结 | In Progress | M1-W2-1.5-PoC 技术审查与口径冻结-In Progress |
| 1.6 | 运维与合规闭环任务 | In Progress | M1-W2-1.6-运维与合规闭环任务-In Progress |
| 1.7 | 发布基线与回滚准入矩阵 | In Progress | M1-W2-1.7-发布基线与回滚准入矩阵-In Progress |
| 1.8 | 周中风险复盘与阻塞治理 | In Progress | M1-W2-1.8-周中风险复盘与阻塞治理-In Progress |

## 3. Task Payload For Notion Body
| task_id | deliverables | acceptance result | evidence links | blocker + ETA |
|---|---|---|---|---|
| 1.1 | 授权登记、闸门检查、脱敏规则、抽检报告 | Passed（未授权样本=0；脱敏覆盖率=100%） | `docs/status/1.1-data-authorization-register.csv`; `docs/status/1.1-access-gate-check.md`; `docs/status/1.1-desensitization-rules-v1.md`; `docs/status/1.1-desensitization-sampling-report.md` | None |
| 1.2 | 规则实现、JSON 报告格式、接口清单 v0.1 | Passed（规则测试通过） | `src/prds_agent/rules/engine.py`; `tests/test_rule_engine.py`; `docs/status/week2-deliverables-2026-03-05.md` | None |
| 1.3 | dataset/manifest/hash/标注手册 | Pending | `docs/status/1.3-test-cases-completion-plan.md`; `docs/status/1.3-test-execution-results.md` | manifest/hash 与样本规模未冻结；ETA 2026-03-31 |
| 1.4 | 压测脚本/三轮原始结果/指标计算说明 | Pending | `docs/status/1.4-performance-baseline-plan.md`; `docs/status/perf-and-ops-baseline.md` | staging压测环境未就绪；ETA 2026-04-01 |
| 1.5 | 技术审查记录/口径冻结确认单 | Pending | `docs/status/1.5-technical-integration-plan.md`; `docs/status/subagent-architecture-design-review-2026-03-05.md` | 依赖 1.3/1.4 初版；ETA 2026-04-02 |
| 1.6 | 告警链路验证/回滚演练/合规检查 | Pending | `docs/status/1.6-1.7-monitoring-alert-plan.md`; `docs/status/devops-baseline-alert-plan.md` | 依赖 1.4 首版；ETA 2026-04-03 |
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
