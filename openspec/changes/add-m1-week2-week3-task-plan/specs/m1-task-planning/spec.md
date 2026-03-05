## ADDED Requirements

### Requirement: M1 Week2/Week3 任务清单必须使用五元组并可追踪
项目 MUST 为 M1 Week2 与 Week3 维护可执行的任务清单。每个任务 MUST 包含：负责人、截止日期、交付物、验收标准、前置依赖。

#### Scenario: 按角色发布周任务
- **WHEN** M1 Week2/Week3 开始前完成排期
- **THEN** 系统提供按角色拆分的任务清单（开发/测试/架构/运维/项目）
- **AND** 每个任务包含完整五元组信息

#### Scenario: 任务状态追踪
- **WHEN** 角色更新任务进展
- **THEN** 项目经理可以查看未完成项、阻塞项和延期项
- **AND** 阻塞超过 24 小时的任务被标记为升级处理

### Requirement: Gate-M1 指标必须有统一测量协议
M1 周任务 MUST 显式绑定 Gate-M1 指标，且 MUST 定义统一测量协议（样本、窗口、并发、环境、统计规则）。

#### Scenario: Gate 指标映射
- **WHEN** 生成 Week2/Week3 任务清单
- **THEN** 清单中包含准确率 `>=80%` 与同步接口 P95 `<=6s` 的达成路径与测量口径
- **AND** 每项指标有对应产出物（测试报告、性能报告、评审记录）

#### Scenario: Gate 前联调与预验收
- **WHEN** 进入 M1 Week3
- **THEN** 团队执行联调、回归与预验收
- **AND** 在 2026-04-10 前形成 Gate-M1 Go/No-Go 结论

### Requirement: P0=0 必须有明确分级与统计规则
项目 MUST 定义 P0/P1/P2 分级标准、统计范围、截止时点和豁免规则，并将其作为 Gate-M1 的执行依据。

#### Scenario: P0 分级可判定
- **WHEN** 缺陷被录入 M1 PoC 缺陷池
- **THEN** 缺陷可依据分级标准被唯一归类为 P0/P1/P2
- **AND** P0 至少覆盖：系统不可用、数据错误/丢失、安全失效、Gate 指标无法测量

#### Scenario: P0=0 可执行
- **WHEN** 到达 Gate-M1 截止时点
- **THEN** 按预定义统计范围与时点计算 P0 数量
- **AND** 若存在 P0 或发生违规豁免，Gate 结论不得为 Go

### Requirement: 24h 升级必须固化 RACI 与 SLA
项目 MUST 对“阻塞超过 24 小时”的情形定义升级触发、RACI 角色分工和响应 SLA。

#### Scenario: 阻塞触发升级
- **WHEN** 任一任务阻塞连续超过 24 小时
- **THEN** PM 在 2 小时内发起升级记录
- **AND** Tech Lead 在 4 小时内给出处置方案

#### Scenario: 升级闭环
- **WHEN** 升级已触发
- **THEN** 24 小时内完成“恢复/降级/No-Go”决策
- **AND** 升级记录包含责任人、时限和结果

### Requirement: Week3 必须预置缓冲与降级策略
M1 Week3 MUST 预留缓冲窗口，并定义范围降级触发条件，降低里程碑交付风险。

#### Scenario: 缓冲窗口启用
- **WHEN** 进入 2026-04-09 缓冲窗口
- **THEN** 团队仅处理 Gate 阻塞项
- **AND** 不得引入新增功能

#### Scenario: 触发范围降级
- **WHEN** 触发预设条件（如 P0 未清零、P95 连续不达标、准确率连续低于阈值）
- **THEN** 按预定义降级方案收缩范围
- **AND** 输出影响评估与回补计划

### Requirement: 运维与合规闭环必须形成可验收产出
M1 周任务 MUST 包含运维与合规相关交付物，并作为 Gate-M1 输入材料。

#### Scenario: 运维链路验收
- **WHEN** 执行 Gate 前准备
- **THEN** 产出告警链路验证和发布回滚演练记录
- **AND** 记录可被 QA 与 PM 复核

#### Scenario: 合规控制验收
- **WHEN** 执行合规检查
- **THEN** 产出 RBAC、审计日志、敏感信息处理的检查结论
- **AND** 不通过项进入阻塞列表并跟踪关闭
