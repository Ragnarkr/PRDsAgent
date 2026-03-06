# 六角色会议协调器技能

## 概述
本技能专为 PRDsAgent 项目开发团队设计，用于自动化协调六角色（产品经理、技术负责人、开发工程师、测试工程师、项目经理、运维工程师）的评审会议。

## 功能特点
- **一键启动会议**：通过简单命令启动完整的六角色评审流程
- **多轮次协作**：六角色按固定顺序进行多轮发言（默认2轮），每轮可回应前序角色观点
- **Codex 子代理优先**：默认使用 `codex_subagent` 模式，由 Codex 会话内 6 个 subagent 执行发言
- **标准化输出**：生成符合大公司标准的会议报告和行动项
- **冲突解决**：内置决策权重机制，自动处理意见分歧
- **MCP风格 Notion 写入**：会议后生成 `notion-create-pages` payload 并入队，交由具备 MCP 能力的宿主执行

## 使用方法
### 基本用法
```
@bot six-role-meeting "讨论PRDsAgent架构设计方案"
```

### 高级用法
```
@bot six-role-meeting --topic "需求文档评审" --document ./docs/spec.md
```

## 配置文件
- `config/roles.yaml`：定义六角色信息和决策权重
- `templates/meeting_report_template.md`：会议报告模板
- `templates/role_prompts/`：各角色专用prompt模板

## Notion 同步配置（新增）

默认开启 MCP 入队，可通过环境变量调整：

- `PRDS_NOTION_AUTO_SYNC`：是否启用自动同步（默认 `true`）
- `PRDS_NOTION_DATA_SOURCE_ID`：目标 data source id（默认：`31a96011-ac3e-80cf-b7a7-000b3e60ab6b`）
- `PRDS_NOTION_TEMPLATE_ID`：会议模板 id（默认：`31b96011-ac3e-8068-803d-f2cdcc7aed77`，即 `会议记录`）
- `PRDS_NOTION_ROLE`：记录页的 `角色` 属性默认值（默认：`项目经理`）
- `PRDS_NOTION_MODULE`：记录页的 `模块` 属性默认值（默认：`项目管理`）
- `PRDS_NOTION_OWNER_ID`：可选，写入 `责任人` 属性的 user id
- `PRDS_NOTION_MCP_QUEUE_DIR`：MCP payload 队列目录（默认：`docs/meeting_reports/notion_mcp_queue`）

## 多轮讨论配置（新增）

- `PRDS_MEETING_ROUNDS`：讨论轮数（默认 `2`）
- `PRDS_MEETING_ENGINE`：`codex_subagent` / `llm` / `mock`（默认 `codex_subagent`）
- `PRDS_MEETING_API_KEY` / `OPENAI_API_KEY`：LLM key（`llm` 模式必需）
- `PRDS_MEETING_BASE_URL`：LLM接口地址（默认 `https://api.openai.com/v1`）
- `PRDS_MEETING_MODEL`：LLM模型名（默认 `gpt-4o-mini`）

### Codex 会话集成说明
- `codex_subagent` 模式需要宿主注入 `subagent_turn_handler` 回调。
- 回调应在每个角色 turn 内：创建/复用对应子代理，传入角色 prompt + 本轮上下文，返回 `opinion/concerns/suggestions`。
- 若未注入回调，协调器会自动降级为 `mock`，以保证流程可执行。

## 输出内容
- 完整的会议纪要
- 各角色的评审意见
- 识别的风险和问题
- 具体的行动项和负责人
- Notion MCP 创建payload（队列文件）

## 技术实现
- 角色讨论引擎支持 `llm`/`mock` 双模式（按轮次驱动）
- 支持多轮次顺序讨论与共享上下文
- Notion 同步采用 MCP payload 入队，交由宿主执行真正写入
- 完善的错误处理和恢复机制

## 适用场景
- PRDsAgent 项目内部评审会议
- 需求文档质量评估
- 架构设计方案讨论
- 技术方案决策
- 风险识别和缓解

## 注意事项
- 本技能仅用于 PRDsAgent 项目开发团队协作
- 需要预先配置好六角色信息
- 会议结果会自动保存到项目文档目录
- MCP 入队失败不会中断主流程，结果会在控制台打印失败原因
