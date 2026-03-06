## ADDED Requirements

### Requirement: Multi-Round Six-Role Collaboration
The meeting coordinator SHALL run six role agents in a fixed order for multiple rounds, where each role can respond to prior turns.

#### Scenario: Ordered multi-round discussion
- **WHEN** a meeting is started with `rounds = N`
- **THEN** each round executes all six roles in priority order
- **AND** each role receives shared context including prior turns
- **AND** the meeting result contains per-round turn records

#### Scenario: Subagent mode fallback
- **WHEN** `codex_subagent` engine is selected but no host callback is injected
- **THEN** the coordinator falls back to `mock` engine
- **AND** still completes the full multi-round flow
- **AND** still generates a local meeting report

#### Scenario: LLM mode fallback
- **WHEN** `llm` engine is selected but no valid credentials are available
- **THEN** the coordinator falls back to `mock` engine
- **AND** still completes the full multi-round flow

### Requirement: MCP-Style Notion Sync Payload
The meeting coordinator SHALL produce an MCP-compatible payload for Notion page creation instead of directly calling the Notion HTTP API.

#### Scenario: MCP payload queue success
- **WHEN** Notion auto-sync is enabled and MCP queue sink is available
- **THEN** the coordinator writes a queued JSON payload for `notion-create-pages`
- **AND** payload includes parent data source, template id, and mapped properties
- **AND** meeting result reports queue file path

#### Scenario: MCP sync disabled
- **WHEN** Notion auto-sync is disabled
- **THEN** the coordinator skips payload queueing
- **AND** marks sync status as disabled
- **AND** still writes the local Markdown report

### Requirement: Meeting Result Property Mapping
The coordinator SHALL map meeting outputs into project-defined Notion properties.

#### Scenario: Property mapping in queued payload
- **WHEN** a Notion MCP payload is generated
- **THEN** it contains `名称`, `日期`, `状态`, `模块`, `角色`, `风险等级`, `下一步动作`, and `阻塞问题`
- **AND** `风险等级` is computed deterministically from concern count
- **AND** long summary text is truncated to safe lengths
