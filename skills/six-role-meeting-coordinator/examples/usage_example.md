# 六角色会议协调器使用示例

## 基本用法

### 1. 启动需求文档评审会议
```
@bot six-role-meeting "评审PRDsAgent架构设计方案"
```

**预期输出：**
```
[MEETING] 正在启动六角色会议：评审PRDsAgent架构设计方案

[MEETING] 会议完成！以下是六角色最终评审结果：
- 产品经理：...
- 技术负责人：...
- 开发工程师：...
- 测试工程师：...
- 运维工程师：...
- 项目经理：...

完整会议报告已生成：/root/.openclaw/workspace/PRDsAgent/docs/meeting_reports/meeting_评审PRDsAgent架构设计方案.md
Notion MCP 写入已入队：.../docs/meeting_reports/notion_mcp_queue/notion_mcp_queue_YYYYMMDD-HHMMSS.json
```

### 2. 评审具体文档文件
```
@bot six-role-meeting --topic "需求文档质量评估" --document ./docs/项目愿景.md
```

## 高级用法

### 3. 自定义会议配置
```python
from skills.six_role_meeting_coordinator.meeting_coordinator import SixRoleMeetingCoordinator

def codex_turn_handler(role, system_prompt, user_prompt):
    # 在 Codex 会话内由宿主实现：调用 spawn_agent / send_input / wait
    # 需返回 {"opinion": "...", "concerns": [...], "suggestions": [...]}
    raise NotImplementedError

coordinator = SixRoleMeetingCoordinator(
    rounds=3,
    subagent_turn_handler=codex_turn_handler,
)
result = coordinator.start_meeting(
    topic="PRDsAgent M1阶段技术方案评审",
    document_path="./docs/架构设计文档.md"
)
print(f"会议报告: {result['report_path']}")
```

### 4. 集成到CI/CD流程
```bash
python -m skills.six_role_meeting_coordinator.meeting_coordinator \
    "自动化PRD质量检查" \
    "./docs/latest_prd.md" \
    --rounds 2
```

### 5. 启用 MCP 风格 Notion 写入（入队）
```bash
export PRDS_NOTION_AUTO_SYNC=true
export PRDS_NOTION_DATA_SOURCE_ID=31a96011-ac3e-80cf-b7a7-000b3e60ab6b
export PRDS_NOTION_TEMPLATE_ID=31b96011-ac3e-8068-803d-f2cdcc7aed77
export PRDS_NOTION_MCP_QUEUE_DIR=./docs/meeting_reports/notion_mcp_queue
python -m skills.six_role_meeting_coordinator.meeting_coordinator "M1 启动会议" --rounds 2
```

### 6. 启用 LLM 多轮讨论
```bash
export PRDS_MEETING_ENGINE=llm
export PRDS_MEETING_API_KEY=sk-xxx
export PRDS_MEETING_MODEL=gpt-4o-mini
python -m skills.six_role_meeting_coordinator.meeting_coordinator "M1 启动会议" --rounds 3
```

### 7. 使用 Codex 子代理模式（默认）
```bash
export PRDS_MEETING_ENGINE=codex_subagent
# 由 Codex 宿主注入 subagent_turn_handler；若未注入将自动降级为 mock
python -m skills.six_role_meeting_coordinator.meeting_coordinator "M1 启动会议" --rounds 2
```

## 输出文件结构

会议报告与 MCP payload 队列会生成在以下位置：
```
PRDsAgent/
└── docs/
    └── meeting_reports/
        ├── meeting_*.md
        └── notion_mcp_queue/
            └── notion_mcp_queue_*.json
```

## 注意事项

1. **仅限PRDsAgent项目使用**：本技能专为PRDsAgent开发团队设计
2. **依赖项目结构**：需要在PRDsAgent项目根目录下运行
3. **文件权限**：确保有写入 `docs/meeting_reports/` 目录权限
4. **Notion写入模式**：当前脚本生成 MCP payload 队列，不直接调用 Notion HTTP API
5. **OpenClaw环境**：需要在支持OpenClaw工具的环境中运行

## 故障排除

### 常见问题
- **找不到配置文件**：确保在PRDsAgent项目根目录运行
- **权限错误**：检查 `docs/meeting_reports/` 目录写入权限
- **角色信息不匹配**：更新 `config/roles.yaml` 团队成员信息
- **MCP入队失败**：检查 `PRDS_NOTION_MCP_QUEUE_DIR`、`PRDS_NOTION_DATA_SOURCE_ID`、`PRDS_NOTION_TEMPLATE_ID`
- **讨论结果过于模板化**：启用 `PRDS_MEETING_ENGINE=llm` 并提供可用 API key
