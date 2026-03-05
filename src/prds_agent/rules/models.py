from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class RuleIssue:
    rule_id: str
    category: str
    severity: str
    message: str
    suggestion: str
    evidence: str | None = None
    line_no: int | None = None


@dataclass(slots=True)
class RuleReport:
    source_path: Path
    issues: list[RuleIssue] = field(default_factory=list)

    @property
    def has_blocker(self) -> bool:
        return any(issue.severity == "error" for issue in self.issues)
