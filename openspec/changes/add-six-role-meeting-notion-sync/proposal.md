# Change: Upgrade Six-Role Meeting to Multi-Agent Rounds + MCP Notion Sync

## Why
Current meeting coordinator still behaves like a fast single-pass summarizer in practice, which does not meet the expected six-role roundtable behavior. Also, direct Notion HTTP API writing is not aligned with the project's MCP-first workflow.

## What Changes
- Upgrade the discussion flow to true multi-round, ordered six-role collaboration.
- Keep per-role prompt isolation and pass prior turns as shared context for cross-role responses.
- Support three discussion engines:
  - `codex_subagent`: primary mode, runs role turns through host-provided Codex subagent callback.
  - `llm`: optional fallback with direct model API calls.
  - `mock`: deterministic fallback when no subagent callback or model credentials are available.
- Replace direct Notion HTTP API write with MCP-style sync:
  - build `notion-create-pages` payload,
  - enqueue payload as local JSON for MCP-capable host execution.
- Keep local Markdown report generation as mandatory fallback artifact.

## Impact
- Affected specs: `six-role-meeting-coordination` (new)
- Affected code:
  - `skills/six-role-meeting-coordinator/meeting_coordinator.py`
  - `skills/six-role-meeting-coordinator/SKILL.md`
  - `skills/six-role-meeting-coordinator/examples/usage_example.md`
  - `tests/test_six_role_meeting_coordinator.py`
- Operational impact:
  - meeting output now includes round data and MCP queue status.
  - Notion writes are executed by MCP host, not by this script directly.
