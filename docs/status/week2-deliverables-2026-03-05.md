# M1 Week2 交付补充（2026-03-05）

## 1.2 规则引擎 v1（已完成）

### JSON 报告格式 v0.1
- 根字段：`file`、`section_count`、`issues`
- `issues[*]` 必填字段：
  - `rule_id`
  - `category`
  - `severity`
  - `message`
  - `suggestion`
  - `evidence`
  - `line_no`

### 接口清单 v0.1（冻结）
| 接口 | 输入 | 输出 | 稳定字段 |
|---|---|---|---|
| `DocumentParser.parse(path)` | `path: str` | `ParsedDocument` | `source_path/content/sections` |
| `RuleEngine.analyze(document)` | `ParsedDocument` | `RuleReport` | `issues[*].rule_id/severity/evidence` |
| `python -m prds_agent.cli <file>` | 文档路径 | JSON 报告 | `issues[*]` 字段集合 |

冻结说明：
- `v0.1` 冻结范围仅覆盖 M1 Gate 必需字段，不包含新规则扩展字段。
- 破坏性字段变更需走 24h 升级流程并同步 QA/DevOps。

## 1.4 性能测量脚本与口径（进行中）

已新增可执行脚本模块：`src/prds_agent/metrics/baseline.py`。

运行方式（示例）：
```bash
$env:PYTHONPATH="src"; python -m prds_agent.metrics.baseline round1.jsonl round2.jsonl round3.jsonl
```

输入数据（JSONL）字段：
- `request_id`
- `status_code`
- `latency_ms`
- `timeout`（可选，默认 `false`）
- `attempt`（可选，默认 `1`）

已固化口径：
- 重试计数模式：`latest_attempt` 或 `all_attempts`
- 4xx 成功计数边界：`--count-4xx-as-success` 显式开关
- 指标输出：`p95_ms`、`success_rate`、`error_5xx_rate`、`timeout_rate`
- Gate 汇总：三轮最差值聚合（P95 取最大，其余按门禁方向取最差）

未完成项：
- 三轮真实压测原始结果与环境规格留档（任务 `1.4` 保持进行中）

## 3.2 P0=0 统计规则（已固化）

- 统计范围：仅 `M1 PoC backlog` 内缺陷。
- 截止时点：`2026-04-10 14:00`（逾时变更进入下一周期，不影响本轮 Gate）。
- 分级依据：`docs/status/defect-severity-standard.md`。
- 豁免规则：`P0` 不允许豁免；若出现豁免申请，则 Gate 结论强制为 `No-Go`。
- 输出物：
  - `defect-list.csv`（字段至少含 `id/severity/status/owner/updated_at`）
  - `gate-lock-record.md`（记录锁定时间、统计人、复核人、结论）
