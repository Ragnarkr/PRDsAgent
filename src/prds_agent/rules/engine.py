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

COMPLETENESS_KEYWORDS = {
    "目标": ("目标", "核心目标", "goal", "objective"),
    "范围": ("范围", "in-scope", "out-of-scope", "scope"),
    "依赖": ("依赖", "前置条件", "dependency", "dependencies"),
    "验收标准": ACCEPTANCE_KEYWORDS,
}

METRIC_PATTERN = re.compile(
    r"(?P<metric>[\u4e00-\u9fa5A-Za-z][\u4e00-\u9fa5A-Za-z0-9_/\-\s]{0,30}?)\s*"
    r"(?P<op><=|>=|<|>)\s*(?P<value>\d+(?:\.\d+)?)\s*(?P<unit>%|ms|s|秒|分钟|小时|天)?",
    flags=re.IGNORECASE,
)


class RuleEngine:
    """Week 1 rule engine skeleton for PRD quality checks."""

    def analyze(self, document: ParsedDocument) -> RuleReport:
        issues: list[RuleIssue] = []
        issues.extend(self.check_completeness(document))
        issues.extend(self.check_acceptance_criteria(document))
        issues.extend(self.detect_basic_conflicts(document))
        issues.extend(self.detect_fuzzy_terms(document))
        return RuleReport(source_path=document.source_path, issues=issues)

    def check_completeness(self, document: ParsedDocument) -> list[RuleIssue]:
        text_lower = document.content.lower()
        missing_categories: list[str] = []

        for category, keywords in COMPLETENESS_KEYWORDS.items():
            if not any(keyword in text_lower for keyword in keywords):
                missing_categories.append(category)

        if not missing_categories:
            return []

        return [
            RuleIssue(
                rule_id="CM001",
                category="completeness_check",
                severity="warning",
                message=f"需求完整性缺失：{', '.join(missing_categories)}",
                suggestion="补充目标、范围、依赖、验收标准等关键要素。",
                evidence=document.content[:120],
            )
        ]

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

    def detect_basic_conflicts(self, document: ParsedDocument) -> list[RuleIssue]:
        constraints: dict[str, list[tuple[str, float, int, str]]] = {}

        for line_no, line in enumerate(document.content.splitlines(), start=1):
            for match in METRIC_PATTERN.finditer(line):
                metric = _normalize_metric(match.group("metric"))
                op = match.group("op")
                value = float(match.group("value"))
                unit = (match.group("unit") or "").lower()
                key = f"{metric}|{unit}"
                constraints.setdefault(key, []).append((op, value, line_no, line.strip()))

        issues: list[RuleIssue] = []
        for metric_key, entries in constraints.items():
            lower_bounds = [entry for entry in entries if entry[0] in (">", ">=")]
            upper_bounds = [entry for entry in entries if entry[0] in ("<", "<=")]
            for lower in lower_bounds:
                for upper in upper_bounds:
                    if _is_conflict(lower[0], lower[1], upper[0], upper[1]):
                        metric_name = metric_key.split("|", maxsplit=1)[0]
                        issues.append(
                            RuleIssue(
                                rule_id="CF001",
                                category="conflict_detection",
                                severity="error",
                                message=f"检测到数值冲突：指标[{metric_name}]约束互斥。",
                                suggestion="统一该指标的上下界，避免相互矛盾。",
                                evidence=f"L{lower[2]}: {lower[3]} | L{upper[2]}: {upper[3]}",
                                line_no=min(lower[2], upper[2]),
                            )
                        )
                        break
                else:
                    continue
                break

        return issues

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


def _normalize_metric(metric: str) -> str:
    return re.sub(r"\s+", "", metric).lower()


def _is_conflict(lower_op: str, lower_val: float, upper_op: str, upper_val: float) -> bool:
    if lower_val > upper_val:
        return True
    if lower_val < upper_val:
        return False
    # lower_val == upper_val
    return not (lower_op == ">=" and upper_op == "<=")
