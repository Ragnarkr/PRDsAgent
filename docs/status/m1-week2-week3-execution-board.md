# M1 Week2/Week3 执行总看板（PM）

## 1. 全任务清单（状态更新：2026-03-06）

| 任务ID | 负责人 | 截止日期 | 前置依赖 | 状态 |
|---|---|---|---|---|
| 1.1 | 孙嘉宁 + 赵雨桐 | 2026-03-31 | 无 | Completed |
| 1.2 | 王浩然 | 2026-04-02 | Week1 分支合入 | Completed |
| 1.3 | 赵雨桐 | 2026-04-03 | 1.1, 1.2 | Completed |
| 1.4 | 孙嘉宁 | 2026-04-03 | 1.2 | Completed |
| 1.5 | 李承泽 | 2026-04-04 | 1.3, 1.4 | Completed |
| 1.6 | 孙嘉宁 | 2026-04-05 | 1.4 | Completed |
| 1.7 | 孙嘉宁 + 李承泽 | 2026-04-05 | 1.4, 1.6 | Completed |
| 1.8 | 周明远 | 2026-04-05 | 1.2~1.7 | Completed |
| 2.1 | 王浩然 + 赵雨桐 | 2026-04-08 | Week2 关键项完成 | Completed |
| 2.2 | 赵雨桐 + 孙嘉宁 | 2026-04-09 12:00 | 2.1 | Completed |
| 2.3 | 孙嘉宁 | 2026-04-09 | 1.6 | Completed |
| 2.4 | 周明远 + 李承泽 | 2026-04-08 18:00 | 2.1 + 2.2 首轮签收 | Completed |
| 2.5 | 周明远 | 2026-04-09 18:00 | 2.3, 2.4 | Completed |
| 2.6 | 周明远 | 2026-04-10 16:00 | 2.2, 2.3, 2.4 | Completed |
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

- [x] PM 建立 Notion 主看板并完成回填留痕
- [x] 各负责人确认任务五元组与依赖关系
- [x] Tech Lead 组织 30 分钟“口径冻结预对齐会”
- [x] DevOps 准备压测环境与告警演练环境
- [x] QA 启动数据授权与脱敏前置检查

## 6. 完成证据链接

- `1.1`：`docs/status/1.1-data-authorization-register.csv`、`docs/status/1.1-access-gate-check.md`、`docs/status/1.1-desensitization-rules-v1.md`、`docs/status/1.1-desensitization-sampling-report.md`
- `1.2`：`src/prds_agent/rules/engine.py`、`tests/test_rule_engine.py`、`docs/status/week2-deliverables-2026-03-05.md`
- `1.6`：`docs/status/1.6-1.7-monitoring-alert-plan.md`、`docs/status/1.6-ops-compliance-closure-2026-03-06.md`、`docs/status/ops-drill/ops_alert_delivery_20260306.md`、`docs/status/ops-drill/ops_rollback_drill_20260306.md`
- `1.7`：`docs/status/release-rollback-gate.md`、`docs/status/1.6-1.7-monitoring-alert-plan.md`
- `1.8`：`docs/status/1.8-pm-summary-plan.md`、`docs/status/week2-notion-sync-backfill-2026-03-06.md`
- `2.1`：`docs/status/2.1-poc-integration-regression-report-2026-03-06.md`、`docs/status/2.1-defect-list-2026-03-06.csv`、`docs/status/2.1-defect-closure-report-2026-03-06.md`
- `2.2`：`docs/status/2.2-gate-metrics-retest-2026-03-06.md`、`docs/status/2.2-round1-signoff-2026-03-06.md`、`docs/status/perf-test-data/staging_retest_20260306_2_2_gate_report.json`
- `2.3`：`docs/status/2.3-alert-rollback-final-acceptance-2026-03-06.md`、`docs/status/ops-drill/ops_alert_delivery_20260306_2_3.md`、`docs/status/ops-drill/ops_rollback_drill_20260306_2_3.md`
- `3.1`：`docs/status/defect-severity-standard.md`
- `3.2`：`docs/status/week2-deliverables-2026-03-05.md`

## 7. 状态说明与阻塞（Week2）

- `1.3`（Completed）：`dataset-m1-v1` 已冻结，样本总数=120（Markdown/TXT/DOCX 各40），双人抽检一致率=95.83%，manifest/hash 校验通过。
- `1.4`（Completed）：真实 staging 三轮已完成（500*3，预热50/轮，并发20），最差值结果 `p95=543.316ms / success=100% / 5xx=0% / timeout=0%`，Gate 通过；证据：`docs/status/1.4-performance-real-staging-execution-2026-03-06.md`。
- `1.5`（Completed）：已完成技术评审签字与口径冻结确认（Tech Lead/QA/DevOps/PM 四方签收）；证据：`docs/status/1.5-technical-integration-plan.md`、`docs/status/tech-review-and-freeze.md`。
- `1.6`（Completed）：已完成告警送达率验收（24h样本=24，P1 5分钟内=100%，P2 10分钟内=100%）与真实回滚演练（RTO=2.662s，RPO=0s，回滚后 `/analyze`=200）；证据：`docs/status/1.6-ops-compliance-closure-2026-03-06.md`、`docs/status/ops-drill/ops_alert_delivery_20260306.md`、`docs/status/ops-drill/ops_rollback_drill_20260306.md`。
- `1.7`（Completed）：已完成准入矩阵冻结、阈值口径固化、回滚健康检查验证与 DevOps/Tech Lead/PM 联签；证据：`docs/status/release-rollback-gate.md`。
- `1.8`（Completed）：已完成 Week2 风险复盘与阻塞治理收口，Notion 回填已留痕；证据：`docs/status/1.8-pm-summary-plan.md`。

## 7.1 状态说明与阻塞（Week3）

- `2.1`（Completed）：已完成 PoC 联调回归与缺陷闭环，`pytest -q` 通过（18 passed），基础 API 联调通过，`P0=0`；证据：`docs/status/2.1-poc-integration-regression-report-2026-03-06.md`、`docs/status/2.1-defect-closure-report-2026-03-06.md`。
- `2.1` Notion页：`https://www.notion.so/31b96011ac3e81049442cff54c15dbc6`
- `2.2`（Completed）：已完成三轮 Gate 指标复测与首轮签收，最差值 `accuracy=100% / p95=616.611ms / success=100% / 5xx=0% / timeout=0%`，`P0=0`；证据：`docs/status/2.2-gate-metrics-retest-2026-03-06.md`。
- `2.2` Notion页：`https://www.notion.so/31b96011ac3e81a5ad14d5720aa1b790`
- `2.3`（Completed）：已完成告警与回滚链路最终验收，`P1<=5m=100% / P2<=10m=100% / RTO=3.108s / RPO=0s`，回滚后 `/analyze`=200；证据：`docs/status/2.3-alert-rollback-final-acceptance-2026-03-06.md`。
- `2.3` Notion页：`https://www.notion.so/31b96011ac3e817e8692cd7954d2d7f0`
- `2.4`（Completed）：已完成固定时点降级触发检查，`P0=0`、`P95` 三轮均远低于 `6.5s`、准确率三轮均 `100%`，PM+Tech Lead 联合决议“恢复（不降级，非 No-Go）”；证据：`docs/status/2.4-degrade-trigger-check-and-decision-2026-03-06.md`。
- `2.4` Notion页：`https://www.notion.so/31b96011ac3e8135a45cfeed02c01910`
- `2.5`（Completed）：已完成 Week3 缓冲窗口执行，阻塞项（告警送达/回滚链路/降级触发/功能欠账）均闭环，且未引入新增功能；证据：`docs/status/2.5-week3-buffer-window-execution-2026-03-06.md`。
- `2.5` Notion页：`https://www.notion.so/31b96011ac3e815d9d2dd330964f8601`
- `2.6`（Completed）：已完成 Gate-M1 评审与结论归档，形成 14:00 锁定/15:00 评审/16:00 发布的结构化纪要并发布 `Go` 结论；证据：`docs/status/2.6-gate-m1-review-and-conclusion-2026-03-06.md`。
- `2.6` Notion页：`https://www.notion.so/31b96011ac3e81ce9f9ce0ba8ddc77e3`

## 8. Notion Sync Status (2026-03-06)
- Scope: Week2 tasks `1.1~1.8`
- Status: `Completed` (Notion MCP recovered)
- Backfill package: `docs/status/week2-notion-sync-backfill-2026-03-06.md`
- New backfill pages:
  - `https://www.notion.so/31b96011ac3e818ca57ec3c2c24d9a24`
  - `https://www.notion.so/31b96011ac3e81a7bcd8ebfdae1e8389`

## 8.1 Notion Sync Status (Week3 incremental, 2026-03-06)
- Scope: Week3 tasks `2.1~2.6`
- Status: `Completed` (`2.1~2.6` all synced)
- New pages:
  - `2.1`：`https://www.notion.so/31b96011ac3e81049442cff54c15dbc6`
  - `2.2`：`https://www.notion.so/31b96011ac3e81a5ad14d5720aa1b790`
  - `2.3`：`https://www.notion.so/31b96011ac3e817e8692cd7954d2d7f0`
  - `2.4`：`https://www.notion.so/31b96011ac3e8135a45cfeed02c01910`
  - `2.5`：`https://www.notion.so/31b96011ac3e815d9d2dd330964f8601`
  - `2.6`：`https://www.notion.so/31b96011ac3e81ce9f9ce0ba8ddc77e3`
