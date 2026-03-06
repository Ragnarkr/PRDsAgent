# 六角色会议协调器技能

## 概述
本技能专为 PRDsAgent 项目开发团队设计，用于自动化协调六角色（产品经理、技术负责人、开发工程师、测试工程师、项目经理、运维工程师）的评审会议。

## 功能特点
- **一键启动会议**：通过简单命令启动完整的六角色评审流程
- **自动化协调**：按预设顺序协调各角色发言，维护共享上下文
- **标准化输出**：生成符合大公司标准的会议报告和行动项
- **冲突解决**：内置决策权重机制，自动处理意见分歧

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

## 输出内容
- 完整的会议纪要
- 各角色的评审意见
- 识别的风险和问题
- 具体的行动项和负责人
- Notion任务卡片（可选）

## 技术实现
- 使用 OpenClaw 原生工具：`sessions_spawn`, `sessions_send`, `sessions_history`, `write`
- 支持异步执行，避免超时
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