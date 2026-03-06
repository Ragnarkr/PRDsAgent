# M1 Week2/Week3 执行总看板（PM）

## 1. 全任务清单（状态更新：2026-03-06）

| 任务ID | 负责人 | 截止日期 | 前置依赖 | 状态 |
|---|---|---|---|---|
| 1.1 | 孙嘉宁 + 赵雨桐 | 2026-03-31 | 无 | Completed |
| 1.2 | 王浩然 | 2026-04-02 | Week1 分支合入 | Completed |
| 1.3 | 赵雨桐 | 2026-04-03 | 1.1, 1.2 | Completed |
| 1.4 | 孙嘉宁 | 2026-04-03 | 1.2 | Completed |
| 1.5 | 李承泽 | 2026-04-04 | 1.3, 1.4 | Completed |
| 1.6 | 孙嘉宁 | 2026-04-05 | 1.4 | In Progress |
| 1.7 | 孙嘉宁 + 李承泽 | 2026-04-05 | 1.4, 1.6 | In Progress |
| 1.8 | 周明远 | 2026-04-05 | 1.2~1.7 | In Progress |
| 2.1 | 王浩然 + 赵雨桐 | 2026-04-08 | Week2 关键项完成 | Not Started |
| 2.2 | 赵雨桐 + 孙嘉宁 | 2026-04-09 12:00 | 2.1 | Not Started |
| 2.3 | 孙嘉宁 | 2026-04-09 | 1.6 | Not Started |
| 2.4 | 周明远 + 李承泽 | 2026-04-08 18:00 | 2.1 + 2.2 首轮签收 | Not Started |
| 2.5 | 周明远 | 2026-04-09 18:00 | 2.3, 2.4 | Not Started |
| 2.6 | 周明远 | 2026-04-10 16:00 | 2.2, 2.3, 2.4 | Not Started |
| 3.1 | 赵雨桐 | 2026-04-06 | 无 | Completed |
| 3.2 | 周明远 | 2026-04-06 | 3.1 | Completed |
| 4.1 | 周明远 | 2026-04-07 | 1.8 | Not Started |
| 5.1 | 李承泽 | 2026-04-08 | 2.1 首轮结果 | In Progress |

## 2. 关键路径（阻塞 Gate-M1）

`1.1 -> 1.3 -> 1.5 -> 2.1 -> 2.2 -> 2.4 -> 2.6`

并行关键链：
- `1.2 -> 1.4 -> 1.6 -> 2.3 -> 2.6`
- `3.1 -> 3.2 -> 2.6`

## 3. 固定检查点

- 2026-04-08 16:00：首轮复测签收（2.2）
- 2026-04-08 18:00：降级触发检查与决策（2.4）
- 2026-04-10 14:00：P0 与指标锁定（3.2/2.2）
- 2026-04-10 15:00：Gate 评审会
- 2026-04-10 16:00：发布 Go/No-Go 结论（2.6）

## 4. 24h 升级机制执行说明

- 触发条件：
  - 阻塞连续超过 24h
  - Gate 指标连续两轮不达标
  - 截止检查点仍有 P0
- SLA：
  - 2h 内：PM 发起升级记录
  - 4h 内：Tech Lead 输出技术处置方案
  - 24h 内：完成恢复/降级/No-Go 决策

## 5. 今日启动动作（2026-03-05）

- [ ] PM 建立 Notion 主看板并挂载本文件链接
- [x] 各负责人确认任务五元组与依赖关系
- [x] Tech Lead 组织 30 分钟“口径冻结预对齐会”
- [x] DevOps 准备压测环境与告警演练环境
- [x] QA 启动数据授权与脱敏前置检查

## 6. 完成证据链接

- `1.1`：`docs/status/1.1-data-authorization-register.csv`、`docs/status/1.1-access-gate-check.md`、`docs/status/1.1-desensitization-rules-v1.md`、`docs/status/1.1-desensitization-sampling-report.md`
- `1.2`：`src/prds_agent/rules/engine.py`、`tests/test_rule_engine.py`、`docs/status/week2-deliverables-2026-03-05.md`
- `3.1`：`docs/status/defect-severity-standard.md`
- `3.2`：`docs/status/week2-deliverables-2026-03-05.md`

## 7. 状态说明与阻塞（Week2）

- `1.3`（Completed）：`dataset-m1-v1` 已冻结，样本总数=120（Markdown/TXT/DOCX 各40），双人抽检一致率=95.83%，manifest/hash 校验通过。
- `1.4`（Completed）：真实 staging 三轮已完成（500*3，预热50/轮，并发20），最差值结果 `p95=543.316ms / success=100% / 5xx=0% / timeout=0%`，Gate 通过；证据：`docs/status/1.4-performance-real-staging-execution-2026-03-06.md`。
- `1.5`（Completed）：已完成技术评审签字与口径冻结确认（Tech Lead/QA/DevOps/PM 四方签收）；证据：`docs/status/1.5-technical-integration-plan.md`、`docs/status/tech-review-and-freeze.md`。
- `1.6`（In Progress）：`1.4` 前置已满足，当前待完成告警链路验收与回滚演练首轮记录；ETA：2026-04-03 完成首轮演练。
- `1.7`（In Progress）：`1.4` 前置已满足，当前待 `1.6` 演练结果确认后完成准入矩阵联签；ETA：2026-04-04 完成准入矩阵初版。
- `1.8`（In Progress）：阻塞项为依赖 `1.3~1.7` 阻塞闭环；ETA：2026-04-05 完成 Week2 收口。

## 8. Notion Sync Blocker (2026-03-06)
- Scope: Week2 tasks `1.1~1.8`
- Status: `Blocked` (Notion integration channel)
- Blocker detail: Notion MCP handshake failed when initializing `https://mcp.notion.com/mcp`
- Local source of truth during outage: `openspec/changes/add-m1-week2-week3-task-plan/tasks.md` + this execution board
- Backfill package: `docs/status/week2-notion-sync-backfill-2026-03-06.md`
- Recovery SLA: after MCP恢复, 30 minutes 内完成 Notion 回填
