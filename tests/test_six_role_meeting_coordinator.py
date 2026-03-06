from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = (
    ROOT / "skills" / "six-role-meeting-coordinator" / "meeting_coordinator.py"
)

spec = importlib.util.spec_from_file_location("meeting_coordinator", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec is not None and spec.loader is not None
spec.loader.exec_module(module)

MockDiscussionEngine = module.MockDiscussionEngine
SixRoleMeetingCoordinator = module.SixRoleMeetingCoordinator


def test_multi_round_discussion_order_and_count(tmp_path):
    coordinator = SixRoleMeetingCoordinator(
        project_root=str(tmp_path),
        rounds=2,
        engine=MockDiscussionEngine(),
    )

    result = coordinator.start_meeting(topic="多轮讨论测试")

    assert result["rounds"] == 2
    assert result["engine_mode"] == "mock"
    assert len(result["round_data"]) == 2

    expected_order = [
        "产品经理",
        "技术负责人",
        "开发工程师",
        "测试工程师",
        "运维工程师",
        "项目经理",
    ]

    for round_item in result["round_data"]:
        turns = round_item["turns"]
        assert len(turns) == 6
        display_order = [turn["display_name"] for turn in turns]
        assert display_order == expected_order


def test_build_notion_mcp_payload_contains_template_and_properties(tmp_path):
    coordinator = SixRoleMeetingCoordinator(
        project_root=str(tmp_path),
        rounds=1,
        engine=MockDiscussionEngine(),
    )
    result = coordinator.start_meeting(topic="MCP payload测试")

    queue_file = Path(result["notion_sync"]["queue_file"])
    payload = json.loads(queue_file.read_text(encoding="utf-8"))

    assert payload["tool"] == "notion-create-pages"
    assert payload["parent"]["data_source_id"]
    assert payload["pages"][0]["template_id"]

    props = payload["pages"][0]["properties"]
    required = {
        "名称",
        "date:日期:start",
        "date:日期:is_datetime",
        "状态",
        "模块",
        "角色",
        "风险等级",
        "下一步动作",
        "阻塞问题",
    }
    assert required.issubset(set(props.keys()))


def test_notion_mcp_sync_disabled(monkeypatch, tmp_path):
    monkeypatch.setenv("PRDS_NOTION_AUTO_SYNC", "false")
    coordinator = SixRoleMeetingCoordinator(
        project_root=str(tmp_path),
        rounds=1,
        engine=MockDiscussionEngine(),
    )

    result = coordinator.start_meeting(topic="禁用MCP同步测试")

    assert result["notion_sync"]["status"] == "disabled"
    assert "PRDS_NOTION_AUTO_SYNC=false" in result["notion_sync"]["reason"]


def test_notion_mcp_queue_file_created(tmp_path):
    coordinator = SixRoleMeetingCoordinator(
        project_root=str(tmp_path),
        rounds=1,
        engine=MockDiscussionEngine(),
    )

    result = coordinator.start_meeting(topic="队列落盘测试")

    assert result["notion_sync"]["status"] == "queued"
    queue_file = Path(result["notion_sync"]["queue_file"])
    assert queue_file.exists()


def test_codex_subagent_callback_engine(monkeypatch, tmp_path):
    monkeypatch.setenv("PRDS_MEETING_ENGINE", "codex_subagent")

    def _turn_handler(role, system_prompt, user_prompt):
        _ = system_prompt
        _ = user_prompt
        return {
            "opinion": f"{role['display_name']} 回调输出",
            "concerns": ["关注点A"],
            "suggestions": ["建议A"],
        }

    coordinator = SixRoleMeetingCoordinator(
        project_root=str(tmp_path),
        rounds=1,
        subagent_turn_handler=_turn_handler,
    )
    result = coordinator.start_meeting(topic="subagent回调测试")

    assert result["engine_mode"] == "codex_subagent"
    first_round = result["round_data"][0]["turns"]
    assert first_round[0]["opinion"] == "产品经理 回调输出"
