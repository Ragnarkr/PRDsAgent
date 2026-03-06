#!/usr/bin/env python3
"""
六角色会议协调器 - PRDsAgent 项目专用

实现目标：
1) 六角色按固定顺序进行多轮次讨论（非单轮模拟）。
2) 会议结果输出本地 Markdown 报告。
3) Notion 写入改为 MCP 风格：生成 notion-create-pages 的 payload 入队，
   由具备 MCP 能力的宿主执行真正写入。
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional, Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def _env_flag(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


class DiscussionEngine(Protocol):
    """角色讨论引擎协议。"""

    def generate(self, role: Dict, system_prompt: str, user_prompt: str) -> Dict:
        """生成单个角色本轮输出。"""


class MockDiscussionEngine:
    """本地兜底引擎：无外部模型时仍可演示完整多轮流程。"""
    mode = "mock"

    _BASE = {
        "product_manager": {
            "opinion": "需求目标总体清晰，但验收标准还需进一步量化。",
            "concerns": ["关键指标口径不统一", "范围边界定义不够严格"],
            "suggestions": ["补齐量化验收指标", "增加里程碑验收门槛"],
        },
        "tech_lead": {
            "opinion": "技术路线可行，但需控制集成复杂度与风险扩散。",
            "concerns": ["模块边界耦合偏高", "回滚路径演练不足"],
            "suggestions": ["先冻结接口契约", "补一次回滚演练"],
        },
        "developer": {
            "opinion": "实现工作量可控，但需要提前锁定依赖与排期。",
            "concerns": ["依赖版本未完全冻结", "异常场景处理条目不足"],
            "suggestions": ["先做技术验证分支", "补齐异常路径任务卡"],
        },
        "qa_engineer": {
            "opinion": "测试策略方向正确，但边界与异常覆盖仍需加强。",
            "concerns": ["边界条件覆盖不完整", "回归基线缺少版本标识"],
            "suggestions": ["建立固定回归清单", "增加风险项回归样例"],
        },
        "devops_engineer": {
            "opinion": "运维准备基本可行，但监控和告警策略需要前置。",
            "concerns": ["关键告警SLA未固化", "容量预估缺少压测支撑"],
            "suggestions": ["补全监控指标矩阵", "完成压测并校准阈值"],
        },
        "project_manager": {
            "opinion": "进度可推进，但需强化阻塞升级机制和资源协同。",
            "concerns": ["跨角色依赖闭环不足", "阻塞升级触发条件不够可执行"],
            "suggestions": ["建立每日阻塞看板", "固化24h/48h升级动作"],
        },
    }

    def generate(self, role: Dict, system_prompt: str, user_prompt: str) -> Dict:
        role_name = role["name"]
        base = self._BASE.get(
            role_name,
            {"opinion": "无特殊意见", "concerns": [], "suggestions": []},
        )

        round_no = 1
        for line in user_prompt.splitlines():
            if line.startswith("ROUND:"):
                try:
                    round_no = int(line.split(":", 1)[1].strip())
                except ValueError:
                    round_no = 1
                break

        opinion = base["opinion"]
        if round_no > 1:
            opinion = f"第{round_no}轮补充：{opinion}"

        return {
            "opinion": opinion,
            "concerns": base["concerns"][:3],
            "suggestions": base["suggestions"][:3],
        }


class ChatCompletionDiscussionEngine:
    """基于 Chat Completions 的角色讨论引擎。"""
    mode = "llm"

    def __init__(self, api_key: str, model: str, base_url: str) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")

    @classmethod
    def from_env(cls) -> Optional["ChatCompletionDiscussionEngine"]:
        api_key = os.getenv("PRDS_MEETING_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None

        model = os.getenv("PRDS_MEETING_MODEL", "gpt-4o-mini")
        base_url = os.getenv("PRDS_MEETING_BASE_URL", "https://api.openai.com/v1")
        return cls(api_key=api_key, model=model, base_url=base_url)

    def generate(self, role: Dict, system_prompt: str, user_prompt: str) -> Dict:
        response_text = self._chat_completion(system_prompt=system_prompt, user_prompt=user_prompt)
        parsed = self._parse_json_object(response_text)

        return {
            "opinion": str(parsed.get("opinion", "无特殊意见")).strip(),
            "concerns": self._normalize_list(parsed.get("concerns", [])),
            "suggestions": self._normalize_list(parsed.get("suggestions", [])),
        }

    def _chat_completion(self, system_prompt: str, user_prompt: str) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": (
                        "请仅输出 JSON，不要输出额外文字。格式: "
                        '{"opinion":"...","concerns":["..."],"suggestions":["..."]}\n\n'
                        + user_prompt
                    ),
                },
            ],
            "temperature": 0.2,
        }

        req = Request(
            url=f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            method="POST",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )

        try:
            with urlopen(req, timeout=40) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"LLM HTTP {exc.code}: {details}") from exc
        except URLError as exc:
            raise RuntimeError(f"LLM connection failed: {exc}") from exc

        choices = data.get("choices", [])
        if not choices:
            raise RuntimeError("LLM response missing choices")
        message = choices[0].get("message", {})
        content = message.get("content", "")
        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("LLM response content empty")
        return content

    def _parse_json_object(self, text: str) -> Dict:
        stripped = text.strip()
        try:
            value = json.loads(stripped)
            if isinstance(value, dict):
                return value
        except json.JSONDecodeError:
            pass

        start = stripped.find("{")
        end = stripped.rfind("}")
        if start != -1 and end != -1 and end > start:
            snippet = stripped[start : end + 1]
            try:
                value = json.loads(snippet)
                if isinstance(value, dict):
                    return value
            except json.JSONDecodeError:
                pass

        raise RuntimeError(f"LLM JSON parse failed: {stripped[:180]}")

    def _normalize_list(self, value: object) -> List[str]:
        if not isinstance(value, list):
            return []
        normalized: List[str] = []
        for item in value:
            text = str(item).strip()
            if text:
                normalized.append(text)
            if len(normalized) >= 3:
                break
        return normalized


class CallbackDiscussionEngine:
    """Codex 子代理引擎：通过宿主注入的回调执行每个角色 turn。"""

    mode = "codex_subagent"

    def __init__(self, turn_handler: Callable[[Dict, str, str], Dict]) -> None:
        self.turn_handler = turn_handler

    def generate(self, role: Dict, system_prompt: str, user_prompt: str) -> Dict:
        output = self.turn_handler(role, system_prompt, user_prompt)
        if not isinstance(output, dict):
            raise RuntimeError("Subagent turn handler must return dict")
        return output


class NotionMcpSink(Protocol):
    """MCP 写入接口。"""

    def create_page(self, payload: Dict) -> Dict:
        """执行页面创建。"""


class FileQueueMcpSink:
    """将 Notion MCP payload 入队到本地文件，供具备 MCP 能力的宿主异步执行。"""

    def __init__(self, queue_dir: Path) -> None:
        self.queue_dir = queue_dir
        self.queue_dir.mkdir(parents=True, exist_ok=True)

    def create_page(self, payload: Dict) -> Dict:
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        output = self.queue_dir / f"notion_mcp_queue_{ts}.json"
        with open(output, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)
        return {"status": "queued", "queue_file": str(output)}


class SixRoleMeetingCoordinator:
    """六角色会议协调器主类。"""

    def __init__(
        self,
        project_root: Optional[str] = None,
        rounds: Optional[int] = None,
        engine: Optional[DiscussionEngine] = None,
        subagent_turn_handler: Optional[Callable[[Dict, str, str], Dict]] = None,
        notion_sink: Optional[NotionMcpSink] = None,
    ):
        default_root = Path(__file__).resolve().parents[2]
        self.project_root = Path(project_root) if project_root else default_root
        self.skills_dir = self.project_root / "skills" / "six-role-meeting-coordinator"
        self.templates_dir = self.skills_dir / "templates"

        self.roles = self._load_roles()
        self.role_prompts = self._load_role_prompts()

        configured_rounds = rounds if rounds is not None else int(os.getenv("PRDS_MEETING_ROUNDS", "2"))
        self.rounds = max(1, configured_rounds)

        self.subagent_turn_handler = subagent_turn_handler
        self.engine = engine or self._build_engine()
        self.engine_mode = getattr(self.engine, "mode", self.engine.__class__.__name__)

        self.notion_enabled = _env_flag("PRDS_NOTION_AUTO_SYNC", True)
        self.notion_data_source_id = os.getenv(
            "PRDS_NOTION_DATA_SOURCE_ID",
            "31a96011-ac3e-80cf-b7a7-000b3e60ab6b",
        )
        self.notion_template_id = os.getenv(
            "PRDS_NOTION_TEMPLATE_ID",
            "31b96011-ac3e-8068-803d-f2cdcc7aed77",
        )

        self.notion_sink = notion_sink or self._build_default_mcp_sink()

    def _build_engine(self) -> DiscussionEngine:
        mode = os.getenv("PRDS_MEETING_ENGINE", "codex_subagent").strip().lower()

        if mode == "codex_subagent":
            if self.subagent_turn_handler is not None:
                return CallbackDiscussionEngine(self.subagent_turn_handler)
            return MockDiscussionEngine()

        if mode == "mock":
            return MockDiscussionEngine()

        if mode == "llm":
            llm_engine = ChatCompletionDiscussionEngine.from_env()
            if llm_engine:
                return llm_engine
            return MockDiscussionEngine()

        return MockDiscussionEngine()

    def _build_default_mcp_sink(self) -> Optional[NotionMcpSink]:
        if not self.notion_enabled:
            return None

        queue_dir = os.getenv(
            "PRDS_NOTION_MCP_QUEUE_DIR",
            str(self.project_root / "docs" / "meeting_reports" / "notion_mcp_queue"),
        )
        return FileQueueMcpSink(Path(queue_dir))

    def _load_roles(self) -> Dict:
        """加载角色配置（当前使用内置默认，避免引入 YAML 依赖）。"""
        return {
            "roles": [
                {
                    "name": "product_manager",
                    "display_name": "产品经理",
                    "person": "陈思远",
                    "priority": 1,
                },
                {
                    "name": "tech_lead",
                    "display_name": "技术负责人",
                    "person": "李承泽",
                    "priority": 2,
                },
                {
                    "name": "developer",
                    "display_name": "开发工程师",
                    "person": "王浩然",
                    "priority": 3,
                },
                {
                    "name": "qa_engineer",
                    "display_name": "测试工程师",
                    "person": "赵雨桐",
                    "priority": 4,
                },
                {
                    "name": "devops_engineer",
                    "display_name": "运维工程师",
                    "person": "孙嘉宁",
                    "priority": 5,
                },
                {
                    "name": "project_manager",
                    "display_name": "项目经理",
                    "person": "周明远",
                    "priority": 6,
                },
            ]
        }

    def _load_role_prompts(self) -> Dict[str, str]:
        prompt_dir = self.templates_dir / "role_prompts"
        role_to_file = {
            "product_manager": "product_manager.md",
            "tech_lead": "tech_lead.md",
            "developer": "developer.md",
            "qa_engineer": "qa_engineer.md",
            "devops_engineer": "devops_engineer.md",
            "project_manager": "project_manager.md",
        }

        prompts: Dict[str, str] = {}
        for role_name, filename in role_to_file.items():
            file_path = prompt_dir / filename
            if file_path.exists():
                prompts[role_name] = file_path.read_text(encoding="utf-8")
            else:
                prompts[role_name] = "你是该角色代表，请给出结构化评审意见。"
        return prompts

    def start_meeting(self, topic: str, document_path: Optional[str] = None) -> Dict:
        print(f"[MEETING] 正在启动六角色会议：{topic}")

        meeting_context = self._prepare_meeting_context(topic, document_path)
        rounds_data = self._run_multi_round_discussion(topic, meeting_context)
        final_results = self._extract_final_results(rounds_data)

        report = self._generate_meeting_report(topic, rounds_data, final_results)
        report_path = self._save_meeting_report(report, topic)

        notion_sync = self._sync_to_notion_mcp(topic, rounds_data, final_results)

        return {
            "success": True,
            "topic": topic,
            "rounds": self.rounds,
            "engine_mode": self.engine_mode,
            "results": final_results,
            "round_data": rounds_data,
            "report_path": str(report_path),
            "summary": self._generate_summary(final_results),
            "notion_sync": notion_sync,
        }

    def _prepare_meeting_context(self, topic: str, document_path: Optional[str]) -> Dict:
        context = {
            "topic": topic,
            "document_path": document_path,
            "project_info": "PRDsAgent - 需求文档质量分析工具",
            "meeting_type": "development_review",
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        }
        if document_path and os.path.exists(document_path):
            with open(document_path, "r", encoding="utf-8") as fh:
                context["document_content"] = fh.read()
        return context

    def _run_multi_round_discussion(self, topic: str, context: Dict) -> List[Dict]:
        rounds_data: List[Dict] = []
        ordered_roles = sorted(self.roles["roles"], key=lambda x: x["priority"])

        for round_index in range(1, self.rounds + 1):
            round_turns: List[Dict] = []
            for role in ordered_roles:
                system_prompt = self.role_prompts.get(role["name"], "")
                user_prompt = self._build_turn_prompt(
                    topic=topic,
                    context=context,
                    round_index=round_index,
                    rounds_data=rounds_data,
                    current_round_turns=round_turns,
                    role=role,
                )

                raw = self.engine.generate(role=role, system_prompt=system_prompt, user_prompt=user_prompt)
                normalized = self._normalize_role_output(raw)

                turn = {
                    "role": role["name"],
                    "display_name": role["display_name"],
                    "person": role["person"],
                    "opinion": normalized["opinion"],
                    "concerns": normalized["concerns"],
                    "suggestions": normalized["suggestions"],
                }
                round_turns.append(turn)

            rounds_data.append({"round": round_index, "turns": round_turns})

        return rounds_data

    def _build_turn_prompt(
        self,
        topic: str,
        context: Dict,
        round_index: int,
        rounds_data: List[Dict],
        current_round_turns: List[Dict],
        role: Dict,
    ) -> str:
        previous_round_summaries: List[str] = []
        for r in rounds_data:
            for t in r["turns"]:
                previous_round_summaries.append(
                    f"- 第{r['round']}轮 {t['display_name']}：{t['opinion']}"
                )

        current_round_summaries = [
            f"- {t['display_name']}：{t['opinion']}" for t in current_round_turns
        ]

        doc_excerpt = str(context.get("document_content", ""))[:1200]

        history_block = previous_round_summaries if previous_round_summaries else ["- 无"]
        current_block = (
            current_round_summaries if current_round_summaries else ["- 你是本轮首位发言"]
        )

        lines = [
            f"TOPIC: {topic}",
            f"ROUND: {round_index}",
            f"TOTAL_ROUNDS: {self.rounds}",
            f"ROLE: {role['display_name']}（{role['person']}）",
            "",
            "项目上下文：",
            f"- 项目：{context.get('project_info', '')}",
            f"- 会议类型：{context.get('meeting_type', '')}",
            "",
            "文档片段（若有）：",
            doc_excerpt if doc_excerpt else "- 无",
            "",
            "历史发言摘要：",
        ] + history_block + [
            "",
            "本轮已发言摘要（你需要在其基础上补充/回应）：",
        ] + current_block + [
            "",
            "输出要求：请给出你本轮的独立观点，并显式回应至少一条已有观点。",
            "字段固定为 opinion/concerns/suggestions。",
        ]

        return "\n".join(lines)

    def _normalize_role_output(self, raw: Dict) -> Dict:
        opinion = str(raw.get("opinion", "无特殊意见")).strip() or "无特殊意见"

        concerns: List[str] = []
        suggestions: List[str] = []

        for key, target in (("concerns", concerns), ("suggestions", suggestions)):
            value = raw.get(key, [])
            if isinstance(value, list):
                for item in value:
                    text = str(item).strip()
                    if text and text not in target:
                        target.append(text)
                    if len(target) >= 3:
                        break

        return {
            "opinion": opinion,
            "concerns": concerns,
            "suggestions": suggestions,
        }

    def _extract_final_results(self, rounds_data: List[Dict]) -> Dict:
        final_results: Dict[str, Dict] = {}
        for round_item in rounds_data:
            for turn in round_item["turns"]:
                final_results[turn["role"]] = {
                    "display_name": turn["display_name"],
                    "person": turn["person"],
                    "opinion": turn["opinion"],
                    "concerns": turn["concerns"],
                    "suggestions": turn["suggestions"],
                }
        return final_results

    def _generate_meeting_report(self, topic: str, rounds_data: List[Dict], final_results: Dict) -> str:
        lines: List[str] = []
        lines.append("# PRDsAgent 多角色会议报告")
        lines.append(f"## 会议主题：{topic}")
        lines.append(f"## 会议时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"## 讨论轮次：{self.rounds}")
        lines.append("")

        lines.append("## 轮次讨论记录")
        lines.append("")
        for round_item in rounds_data:
            lines.append(f"### 第{round_item['round']}轮")
            for turn in round_item["turns"]:
                lines.append(f"- **{turn['display_name']}（{turn['person']}）**：{turn['opinion']}")
            lines.append("")

        lines.append("## 最终角色意见")
        lines.append("")
        for role_name, result in final_results.items():
            _ = role_name
            lines.append(f"### {result['display_name']}（{result['person']}）")
            lines.append(f"**意见**：{result['opinion']}")
            if result["concerns"]:
                lines.append("**关注点**：")
                for item in result["concerns"]:
                    lines.append(f"- {item}")
            if result["suggestions"]:
                lines.append("**建议**：")
                for item in result["suggestions"]:
                    lines.append(f"- {item}")
            lines.append("")

        concerns = self._collect_items(final_results, "concerns")
        suggestions = self._collect_items(final_results, "suggestions")

        lines.append("## 汇总结论")
        lines.append("- 当前项目可按既定节奏推进，但需对验收标准、风险升级和回滚链路做前置固化。")
        lines.append("- 需持续关注跨角色依赖闭环，避免关键阻塞在后期集中暴露。")
        lines.append("")

        lines.append("## 关键风险")
        if concerns:
            for item in concerns:
                lines.append(f"- {item}")
        else:
            lines.append("- 暂无")
        lines.append("")

        lines.append("## 行动项")
        lines.append("| 任务描述 | 负责人 | 截止日期 |")
        lines.append("|---|---|---|")
        for idx, item in enumerate(suggestions[:6], start=1):
            lines.append(f"| A-{idx:02d} {item} | 待分配 | 待定 |")

        return "\n".join(lines)

    def _save_meeting_report(self, report: str, topic: str) -> Path:
        reports_dir = self.project_root / "docs" / "meeting_reports"
        reports_dir.mkdir(parents=True, exist_ok=True)

        safe_topic = topic.replace(" ", "_").replace("/", "_")
        filename = f"meeting_{safe_topic}.md"
        output = reports_dir / filename

        with open(output, "w", encoding="utf-8") as fh:
            fh.write(report)

        return output

    def _sync_to_notion_mcp(self, topic: str, rounds_data: List[Dict], final_results: Dict) -> Dict:
        if not self.notion_enabled:
            return {"status": "disabled", "reason": "PRDS_NOTION_AUTO_SYNC=false"}

        if not self.notion_sink:
            return {"status": "disabled", "reason": "No MCP sink configured"}

        payload = self._build_notion_mcp_payload(topic, rounds_data, final_results)

        try:
            result = self.notion_sink.create_page(payload)
            status = result.get("status", "queued")
            return {"status": status, **result}
        except Exception as exc:  # noqa: BLE001
            return {"status": "failed", "reason": str(exc)}

    def _build_notion_mcp_payload(self, topic: str, rounds_data: List[Dict], final_results: Dict) -> Dict:
        concerns = self._collect_items(final_results, "concerns")
        suggestions = self._collect_items(final_results, "suggestions")
        risk_level = self._risk_level_from_concerns(len(concerns))

        local_date = datetime.now().strftime("%Y-%m-%d")
        meeting_title = self._truncate(f"会议记录｜{topic}｜{local_date}", 120)

        blockers = self._truncate("；".join(concerns) if concerns else "无", 1800)
        next_actions = self._truncate("；".join(suggestions) if suggestions else "无", 1800)

        properties: Dict = {
            "名称": meeting_title,
            "date:日期:start": local_date,
            "date:日期:is_datetime": 0,
            "状态": "已完成",
            "模块": os.getenv("PRDS_NOTION_MODULE", "项目管理"),
            "角色": os.getenv("PRDS_NOTION_ROLE", "项目经理"),
            "风险等级": risk_level,
            "下一步动作": next_actions,
            "阻塞问题": blockers,
        }

        owner_id = os.getenv("PRDS_NOTION_OWNER_ID")
        if owner_id:
            properties["责任人"] = [owner_id]

        return {
            "tool": "notion-create-pages",
            "parent": {"data_source_id": self.notion_data_source_id},
            "pages": [
                {
                    "template_id": self.notion_template_id,
                    "properties": properties,
                }
            ],
            "metadata": {
                "topic": topic,
                "rounds": self.rounds,
                "generated_at": datetime.now().isoformat(timespec="seconds"),
                "report_hint": str(self.project_root / "docs" / "meeting_reports"),
                "round_data": rounds_data,
            },
        }

    def _collect_items(self, results: Dict, key: str) -> List[str]:
        seen: set[str] = set()
        merged: List[str] = []
        for result in results.values():
            items = result.get(key, [])
            if not isinstance(items, list):
                continue
            for item in items:
                text = str(item).strip()
                if not text or text in seen:
                    continue
                seen.add(text)
                merged.append(text)
        return merged

    def _risk_level_from_concerns(self, concern_count: int) -> str:
        if concern_count >= 8:
            return "高"
        if concern_count >= 4:
            return "中"
        return "低"

    def _truncate(self, text: str, max_chars: int) -> str:
        if len(text) <= max_chars:
            return text
        return f"{text[: max_chars - 3]}..."

    def _generate_summary(self, final_results: Dict) -> str:
        opinions = [str(item.get("opinion", "")).strip() for item in final_results.values()]
        return "；".join([x for x in opinions if x])


def main() -> None:
    parser = argparse.ArgumentParser(description="六角色会议协调器")
    parser.add_argument("topic", help="会议主题")
    parser.add_argument("document_path", nargs="?", default=None, help="可选文档路径")
    parser.add_argument("--rounds", type=int, default=None, help="讨论轮数，默认取环境变量或2")
    args = parser.parse_args()

    coordinator = SixRoleMeetingCoordinator(rounds=args.rounds)
    result = coordinator.start_meeting(topic=args.topic, document_path=args.document_path)

    print("\n[MEETING] 会议完成！以下是六角色最终评审结果：")
    for role_name, result_data in result["results"].items():
        _ = role_name
        print(f"- {result_data['display_name']}：{result_data['opinion']}")

    print(f"\n完整会议报告已生成：{result['report_path']}")

    notion_sync = result.get("notion_sync", {})
    status = notion_sync.get("status", "unknown")
    if status == "queued":
        print(f"Notion MCP 写入已入队：{notion_sync.get('queue_file', '')}")
    elif status == "disabled":
        print(f"Notion MCP 写入已跳过：{notion_sync.get('reason', '')}")
    elif status == "failed":
        print(f"Notion MCP 写入失败（已保留本地报告）：{notion_sync.get('reason', '')}")
    else:
        print(f"Notion MCP 状态：{status}")


if __name__ == "__main__":
    main()
