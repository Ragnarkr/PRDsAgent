# 1.4 压测基线启动报告（staging-dry-run）

- 生成时间：2026-03-06 13:47:37
- 模式：`dry-run`（用于先完成口径、脚本与产物链路验证）
- 每轮请求：`500`（预热 `50`）
- 并发：`20`
- 时长口径：`10分钟模型`（此报告为离线模拟，不代表真实环境耗时）
- 随机种子：`20260306`

## 原始结果文件
- `docs/status/perf-test-data/staging_dryrun_20260306_round1.jsonl`
- `docs/status/perf-test-data/staging_dryrun_20260306_round2.jsonl`
- `docs/status/perf-test-data/staging_dryrun_20260306_round3.jsonl`

## 分轮指标
| Round | total | success_rate | 5xx_rate | timeout_rate | p95_ms |
|---|---:|---:|---:|---:|---:|
| 1 | 500 | 99.00% | 0.60% | 0.40% | 3603.059 |
| 2 | 500 | 99.60% | 0.40% | 0.00% | 3919.823 |
| 3 | 500 | 99.60% | 0.40% | 0.00% | 3370.346 |

## 最差值 Gate 汇总
- p95_ms(max): `3919.823`（阈值 <= 6000）
- success_rate(min): `99.00%`（阈值 >= 99.00%）
- error_5xx_rate(max): `0.60%`（阈值 <= 0.50%）
- timeout_rate(max): `0.40%`（阈值 <= 0.50%）
- gate_passed: `False`

## 结论
- 已完成三轮原始结果 + 最差值计算的端到端流程打通。
- 当前结果仅作为 1.4 启动证据；正式验收仍需真实 staging 三轮压测与资源水位记录。
