## 1. Implementation
- [x] 1.1 Replace single-pass role simulation with multi-round ordered role discussion flow.
- [x] 1.2 Load and apply per-role prompt templates for each role turn.
- [x] 1.3 Add pluggable discussion engine (`codex_subagent` / `llm` / `mock`) and environment-based selection.
- [x] 1.4 Replace direct Notion API write with MCP-style payload generation + queue sink.
- [x] 1.5 Keep local Markdown report output as mandatory fallback artifact.
- [x] 1.6 Update skill docs and examples to reflect multi-round + MCP workflow.
- [x] 1.7 Add tests for round ordering/count and MCP queue payload output.

## 2. Verification
- [x] 2.1 Run targeted pytest for meeting coordinator tests.
- [x] 2.2 Run full project pytest regression.
- [ ] 2.3 Run one real `codex_subagent` meeting in host-integrated runtime and verify MCP payload generation.
