# 六角色会议协调器使用示例

## 基本用法

### 1. 启动需求文档评审会议
```
@bot six-role-meeting "评审PRDsAgent架构设计方案"
```

**预期输出：**
```
🦀 正在启动六角色会议：评审PRDsAgent架构设计方案

📋 会议完成！以下是六角色评审结果：
- 产品经理：需求目标明确，但验收标准需要更具体
- 技术负责人：技术方案可行，架构设计合理
- 开发工程师：实现复杂度中等，预计需要2周开发时间
- 测试工程师：测试方案基本完整，但缺少边界条件测试
- 运维工程师：部署方案可行，监控指标需要补充
- 项目经理：项目计划合理，资源分配充足

完整会议报告已生成：/root/.openclaw/workspace/PRDsAgent/docs/meeting_reports/meeting_评审PRDsAgent架构设计方案.md
```

### 2. 评审具体文档文件
```
@bot six-role-meeting --topic "需求文档质量评估" --document ./docs/项目愿景.md
```

## 高级用法

### 3. 自定义会议配置
```python
# 在代码中直接调用
from skills.six_role_meeting_coordinator.meeting_coordinator import SixRoleMeetingCoordinator

coordinator = SixRoleMeetingCoordinator()
result = coordinator.start_meeting(
    topic="PRDsAgent M1阶段技术方案评审",
    document_path="./docs/架构设计文档.md"
)
print(f"会议报告: {result['report_path']}")
```

### 4. 集成到CI/CD流程
```bash
# 在CI流程中自动触发会议评审
python -m skills.six_role_meeting_coordinator.meeting_coordinator \
    "自动化PRD质量检查" \
    "./docs/latest_prd.md"
```

## 输出文件结构

会议报告会自动生成在以下位置：
```
PRDsAgent/
└── docs/
    └── meeting_reports/
        ├── meeting_评审PRDsAgent架构设计方案.md
        ├── meeting_需求文档质量评估.md
        └── ...
```

## 配置自定义

### 修改角色信息
编辑 `skills/six-role-meeting-coordinator/config/roles.yaml` 文件来更新团队成员信息。

### 自定义会议模板
修改 `skills/six-role-meeting-coordinator/templates/meeting_report_template.md` 来调整报告格式。

### 调整角色Prompt
在 `skills/six-role-meeting-coordinator/templates/role_prompts/` 目录下修改各角色的评审重点和输出格式。

## 注意事项

1. **仅限PRDsAgent项目使用**：本技能专为PRDsAgent开发团队设计
2. **依赖项目结构**：需要在PRDsAgent项目根目录下运行
3. **文件权限**：确保有写入 `docs/meeting_reports/` 目录的权限
4. **OpenClaw环境**：需要在支持OpenClaw工具的环境中运行

## 故障排除

### 常见问题
- **找不到配置文件**：确保在PRDsAgent项目根目录运行
- **权限错误**：检查 `docs/meeting_reports/` 目录的写入权限
- **角色信息不匹配**：更新 `config/roles.yaml` 中的团队成员信息

### 调试模式
```bash
# 启用详细日志
DEBUG=1 python -m skills.six_role_meeting_coordinator.meeting_coordinator "调试会议"
```