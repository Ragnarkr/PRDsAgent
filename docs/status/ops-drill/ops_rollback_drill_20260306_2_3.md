# 1.6 回滚演练报告

- 执行时间：2026-03-06T15:34:16
- 服务地址：`http://127.0.0.1:8080`
- 回滚触发后恢复耗时（RTO）：`3.108s`（阈值 <= 1800.0s）
- 数据回退窗口（RPO）：`0.0s`（阈值 <= 900.0s）
- 回滚后 analyze 状态码：`200`
- 演练结论：`Passed`

## 证据文件
- `docs/status/ops-drill/ops_rollback_drill_20260306_2_3.json`
- `docs/status/ops-drill/ops_rollback_drill_20260306_2_3_pre_stdout.log`
- `docs/status/ops-drill/ops_rollback_drill_20260306_2_3_pre_stderr.log`
- `docs/status/ops-drill/ops_rollback_drill_20260306_2_3_post_stdout.log`
- `docs/status/ops-drill/ops_rollback_drill_20260306_2_3_post_stderr.log`
