from __future__ import annotations

import argparse
import json

from prds_agent.parsers import DocumentParser
from prds_agent.rules import RuleEngine


def main() -> None:
    parser = argparse.ArgumentParser(description="PRDsAgent Week1 analyzer")
    parser.add_argument("file", help="Path to a markdown/txt/docx document")
    args = parser.parse_args()

    parsed = DocumentParser().parse(args.file)
    report = RuleEngine().analyze(parsed)

    output = {
        "file": str(parsed.source_path),
        "section_count": len(parsed.sections),
        "issues": [
            {
                "rule_id": issue.rule_id,
                "category": issue.category,
                "severity": issue.severity,
                "message": issue.message,
                "suggestion": issue.suggestion,
                "evidence": issue.evidence,
                "line_no": issue.line_no,
            }
            for issue in report.issues
        ],
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
