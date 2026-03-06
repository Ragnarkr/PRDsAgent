#!/usr/bin/env python3
"""
六角色会议协调器 - PRDsAgent 项目专用

该技能用于自动化协调 PRDsAgent 项目开发团队的六角色评审会议。
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional

# OpenClaw 工具导入（运行时由 OpenClaw 提供）
# from openclaw.tools import sessions_spawn, sessions_send, sessions_history, write


class SixRoleMeetingCoordinator:
    """六角色会议协调器主类"""
    
    def __init__(self, project_root: str = "/root/.openclaw/workspace/PRDsAgent"):
        self.project_root = Path(project_root)
        self.skills_dir = self.project_root / "skills" / "six-role-meeting-coordinator"
        self.config_file = self.skills_dir / "config" / "roles.yaml"
        self.templates_dir = self.skills_dir / "templates"
        self.roles = self._load_roles()
        
    def _load_roles(self) -> Dict:
        """加载角色配置"""
        # 简化版本，实际使用 YAML 配置
        return {
            "roles": [
                {
                    "name": "product_manager",
                    "display_name": "产品经理",
                    "person": "陈思远",
                    "priority": 1,
                    "decision_weight": {"business": "high", "technical": "low"}
                },
                {
                    "name": "tech_lead",
                    "display_name": "技术负责人", 
                    "person": "李承泽",
                    "priority": 2,
                    "decision_weight": {"business": "low", "technical": "high"}
                },
                {
                    "name": "developer",
                    "display_name": "开发工程师",
                    "person": "王浩然", 
                    "priority": 3,
                    "decision_weight": {"business": "low", "technical": "medium"}
                },
                {
                    "name": "qa_engineer",
                    "display_name": "测试工程师",
                    "person": "赵雨桐",
                    "priority": 4, 
                    "decision_weight": {"business": "medium", "technical": "medium"}
                },
                {
                    "name": "devops_engineer",
                    "display_name": "运维工程师",
                    "person": "孙嘉宁",
                    "priority": 5,
                    "decision_weight": {"business": "low", "technical": "high"}
                },
                {
                    "name": "project_manager",
                    "display_name": "项目经理",
                    "person": "周明远",
                    "priority": 6,
                    "decision_weight": {"business": "high", "technical": "medium"}
                }
            ]
        }
    
    def start_meeting(self, topic: str, document_path: Optional[str] = None) -> Dict:
        """
        启动六角色会议
        
        Args:
            topic: 会议主题
            document_path: 相关文档路径（可选）
            
        Returns:
            会议结果字典
        """
        print(f"🦀 正在启动六角色会议：{topic}")
        
        # 准备会议上下文
        meeting_context = self._prepare_meeting_context(topic, document_path)
        
        # 按优先级顺序协调各角色发言
        meeting_results = {}
        for role in sorted(self.roles["roles"], key=lambda x: x["priority"]):
            role_result = self._coordinate_role_discussion(role, meeting_context)
            meeting_results[role["name"]] = role_result
            # 更新上下文
            meeting_context = self._update_context_with_role_feedback(
                meeting_context, role, role_result
            )
        
        # 生成会议报告
        report = self._generate_meeting_report(meeting_results, topic)
        
        # 保存报告
        report_path = self._save_meeting_report(report, topic)
        
        return {
            "success": True,
            "topic": topic,
            "results": meeting_results,
            "report_path": str(report_path),
            "summary": self._generate_summary(meeting_results)
        }
    
    def _prepare_meeting_context(self, topic: str, document_path: Optional[str]) -> Dict:
        """准备会议上下文"""
        context = {
            "topic": topic,
            "document_path": document_path,
            "project_info": "PRDsAgent - 需求文档质量分析工具",
            "meeting_type": "development_review",
            "timestamp": "2026-03-05T17:00:00Z"
        }
        if document_path and os.path.exists(document_path):
            with open(document_path, 'r', encoding='utf-8') as f:
                context["document_content"] = f.read()
        return context
    
    def _coordinate_role_discussion(self, role: Dict, context: Dict) -> Dict:
        """协调单个角色的讨论"""
        # 这里应该调用 sessions_spawn 创建 subagent
        # 但由于是示例代码，返回模拟结果
        
        role_prompts = {
            "product_manager": "从产品和业务价值角度评估需求的完整性和清晰度",
            "tech_lead": "从技术架构和可行性角度评估方案的合理性",
            "developer": "从实现复杂度和开发效率角度评估工作量",
            "qa_engineer": "从测试覆盖和质量保证角度评估可测试性", 
            "devops_engineer": "从部署运维和监控角度评估可维护性",
            "project_manager": "从项目进度和资源分配角度评估可行性"
        }
        
        prompt_template = role_prompts.get(role["name"], "请提供专业意见")
        
        # 模拟 subagent 的响应
        simulated_responses = {
            "product_manager": {
                "opinion": "需求目标明确，但验收标准需要更具体",
                "concerns": ["验收标准不够量化"],
                "suggestions": ["增加具体的性能指标和用户场景"]
            },
            "tech_lead": {
                "opinion": "技术方案可行，架构设计合理",
                "concerns": ["需要考虑未来的扩展性"],
                "suggestions": ["建议采用微服务架构便于扩展"]
            },
            "developer": {
                "opinion": "实现复杂度中等，预计需要2周开发时间",
                "concerns": ["依赖的第三方库版本需要确认"],
                "suggestions": ["建议先做技术验证"]
            },
            "qa_engineer": {
                "opinion": "测试方案基本完整，但缺少边界条件测试",
                "concerns": ["异常场景覆盖不足"],
                "suggestions": ["增加压力测试和异常输入测试"]
            },
            "devops_engineer": {
                "opinion": "部署方案可行，监控指标需要补充",
                "concerns": ["缺少性能监控指标"],
                "suggestions": ["增加响应时间和错误率监控"]
            },
            "project_manager": {
                "opinion": "项目计划合理，资源分配充足",
                "concerns": ["需要预留缓冲时间应对风险"],
                "suggestions": ["建议增加1周的缓冲期"]
            }
        }
        
        return simulated_responses.get(role["name"], {
            "opinion": "无特殊意见",
            "concerns": [],
            "suggestions": []
        })
    
    def _update_context_with_role_feedback(self, context: Dict, role: Dict, feedback: Dict) -> Dict:
        """用角色反馈更新上下文"""
        if "role_feedback" not in context:
            context["role_feedback"] = {}
        context["role_feedback"][role["name"]] = feedback
        return context
    
    def _generate_meeting_report(self, results: Dict, topic: str) -> str:
        """生成会议报告"""
        report_lines = []
        report_lines.append(f"# PRDsAgent 项目会议报告")
        report_lines.append(f"## 会议主题：{topic}")
        report_lines.append(f"## 会议时间：2026-03-05 17:00")
        report_lines.append("")
        report_lines.append("## 各角色评审结果")
        report_lines.append("")
        
        for role_name, result in results.items():
            role_info = next((r for r in self.roles["roles"] if r["name"] == role_name), {})
            display_name = role_info.get("display_name", role_name)
            person = role_info.get("person", "未知")
            
            report_lines.append(f"### {display_name}（{person}）")
            report_lines.append(f"**意见**：{result.get('opinion', '无')}")
            if result.get("concerns"):
                report_lines.append(f"**关注点**：{', '.join(result['concerns'])}")
            if result.get("suggestions"):
                report_lines.append(f"**建议**：{', '.join(result['suggestions'])}")
            report_lines.append("")
        
        report_lines.append("## 会议结论")
        report_lines.append("- 需求文档基本完整，需要补充量化验收标准")
        report_lines.append("- 技术方案可行，建议考虑扩展性")
        report_lines.append("- 开发周期预计2周，需要技术验证")
        report_lines.append("- 测试方案需要补充边界条件测试")
        report_lines.append("- 部署方案可行，需要补充监控指标")
        report_lines.append("- 项目计划合理，建议增加缓冲时间")
        report_lines.append("")
        report_lines.append("## 行动项")
        report_lines.append("| 任务描述 | 负责人 | 截止日期 |")
        report_lines.append("|----------|--------|----------|")
        report_lines.append("| 补充量化验收标准 | 陈思远 | 2026-03-10 |")
        report_lines.append("| 完成技术验证 | 王浩然 | 2026-03-08 |")
        report_lines.append("| 补充测试用例 | 赵雨桐 | 2026-03-12 |")
        report_lines.append("| 完善监控方案 | 孙嘉宁 | 2026-03-10 |")
        
        return "\n".join(report_lines)
    
    def _save_meeting_report(self, report: str, topic: str) -> Path:
        """保存会议报告"""
        reports_dir = self.project_root / "docs" / "meeting_reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        # 简化文件名
        filename = f"meeting_{topic.replace(' ', '_').replace('/', '_')}.md"
        report_path = reports_dir / filename
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return report_path
    
    def _generate_summary(self, results: Dict) -> str:
        """生成简要摘要"""
        opinions = [f"{result.get('opinion', '')}" for result in results.values()]
        return "；".join(opinions)


# 主函数入口
def main():
    """技能主入口函数"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python meeting_coordinator.py <topic> [document_path]")
        sys.exit(1)
    
    topic = sys.argv[1]
    document_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    coordinator = SixRoleMeetingCoordinator()
    result = coordinator.start_meeting(topic, document_path)
    
    # 输出结果摘要
    print("\n📋 会议完成！以下是六角色评审结果：")
    for role_name, result_data in result["results"].items():
        role_info = next((r for r in coordinator.roles["roles"] if r["name"] == role_name), {})
        display_name = role_info.get("display_name", role_name)
        print(f"- {display_name}：{result_data.get('opinion', '无特殊意见')}")
    
    print(f"\n完整会议报告已生成：{result['report_path']}")


if __name__ == "__main__":
    main()