from __future__ import annotations

import re

from prds_agent.parsers import ParsedDocument

from .models import RuleIssue, RuleReport

ACCEPTANCE_KEYWORDS = (
    "验收标准",
    "acceptance criteria",
    "given",
    "when",
    "then",
    "必须",
    "应当",
)

FUZZY_TERMS = (
    "尽快",
    "及时",
    "适当",
    "合理",
    "尽量",
    "优化",
    "稳定",
    "友好",
    "高效",
    "等",
)


class RuleEngine:
    """Week 1 rule engine skeleton for PRD quality checks."""

    def analyze(self, document: ParsedDocument) -> RuleReport:
        issues: list[RuleIssue] = []
        issues.extend(self.check_acceptance_criteria(document))
        issues.extend(self.detect_fuzzy_terms(document))
        return RuleReport(source_path=document.source_path, issues=issues)

    def check_acceptance_criteria(self, document: ParsedDocument) -> list[RuleIssue]:
        text_lower = document.content.lower()
        if not any(keyword in text_lower for keyword in ACCEPTANCE_KEYWORDS):
            return [
                RuleIssue(
                    rule_id="AC001",
                    category="acceptance_criteria",
                    severity="error",
                    message="缺少明确的验收标准描述。",
                    suggestion="补充可验证的验收标准（建议采用 Given-When-Then 或量化指标）。",
                )
            ]

        if not _contains_measurement_target(document.content):
            return [
                RuleIssue(
                    rule_id="AC002",
                    category="acceptance_criteria",
                    severity="warning",
                    message="验收标准存在但缺少量化目标。",
                    suggestion="增加明确阈值（例如：响应时间<=3秒、准确率>=90%）。",
                )
            ]
        return []

    def detect_fuzzy_terms(self, document: ParsedDocument) -> list[RuleIssue]:
        issues: list[RuleIssue] = []
        for line_no, line in enumerate(document.content.splitlines(), start=1):
            stripped = line.strip()
            if not stripped:
                continue
            for term in FUZZY_TERMS:
                if term in stripped:
                    issues.append(
                        RuleIssue(
                            rule_id="FT001",
                            category="fuzzy_terms",
                            severity="warning",
                            message=f"检测到模糊词汇: {term}",
                            suggestion="请替换为可度量、可验证的具体表述。",
                            evidence=stripped,
                            line_no=line_no,
                        )
                    )
        return issues


def _contains_measurement_target(text: str) -> bool:
    patterns = (
        r"(>=|<=|>|<)\s*\d+",
        r"\d+\s*%",
        r"\d+\s*(秒|分钟|小时|天)",
        r"p(95|99)",
    )
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)
