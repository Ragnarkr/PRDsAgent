from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from prds_agent.parsers import ParsedDocument, Section
from prds_agent.rules import RuleEngine


class RuleEngineTest(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = RuleEngine()

    def test_missing_acceptance_criteria_returns_error(self) -> None:
        document = ParsedDocument(
            source_path=Path("demo.md"),
            content="这是一个需求说明，没有完成条件定义。",
            sections=[Section(title="全文", level=1, content="这是一个需求说明，没有完成条件定义。")],
        )
        report = self.engine.analyze(document)
        self.assertTrue(any(issue.rule_id == "AC001" for issue in report.issues))

    def test_fuzzy_term_detection(self) -> None:
        document = ParsedDocument(
            source_path=Path("demo.md"),
            content="系统应尽快返回结果，体验要友好。",
            sections=[Section(title="全文", level=1, content="系统应尽快返回结果，体验要友好。")],
        )
        report = self.engine.analyze(document)
        fuzzy_issues = [issue for issue in report.issues if issue.rule_id == "FT001"]
        self.assertGreaterEqual(len(fuzzy_issues), 1)

    def test_quantified_acceptance_criteria(self) -> None:
        content = "验收标准: API响应时间<=3秒，准确率>=90%"
        document = ParsedDocument(
            source_path=Path("demo.md"),
            content=content,
            sections=[Section(title="验收标准", level=1, content=content)],
        )
        report = self.engine.analyze(document)
        self.assertFalse(any(issue.rule_id == "AC001" for issue in report.issues))
        self.assertFalse(any(issue.rule_id == "AC002" for issue in report.issues))


if __name__ == "__main__":
    unittest.main()
