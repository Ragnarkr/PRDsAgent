---
name: prdsagent-m1-gate-evidence
description: Complete PRDsAgent M1 task 1.1 ("data authorization and desensitization pre-gate") with a minimum acceptance package. Use when asked to create the 4 evidence files under docs/status, run the mandatory authorization/desensitization validations, write validation results into reports, and backfill task status in openspec tasks.md and the M1 execution board. This skill is project-specific and must only be used in E:\\porjects\\PRDsAgent.
---

# PRDsAgent M1 Gate Evidence

## Overview

Execute the minimum acceptable package for task `1.1`:
1. Create/update four evidence files.
2. Run two mandatory checks and write results into reports.
3. Backfill progress in `tasks.md` and `m1-week2-week3-execution-board.md`.

## Guardrails

- Only use this skill inside the PRDsAgent repository root.
- Keep outputs under `docs/status/`.
- Treat this skill as project-only, not global.
- Do not change unrelated task statuses.

## Quick Start

Run from repository root:

```powershell
# 1) Create the four required evidence files (if missing)
powershell -ExecutionPolicy Bypass -File .\skills\prdsagent-m1-gate-evidence\scripts\init_1_1_evidence_files.ps1

# 2) Run required validations and write results into reports
powershell -ExecutionPolicy Bypass -File .\skills\prdsagent-m1-gate-evidence\scripts\run_1_1_validations.ps1 -WriteReports
```

After running, backfill status files using the instructions below.

## Required Evidence Files

The minimum package must include:

1. `docs/status/1.1-data-authorization-register.csv`
2. `docs/status/1.1-access-gate-check.md`
3. `docs/status/1.1-desensitization-rules-v1.md`
4. `docs/status/1.1-desensitization-sampling-report.md`

Template guidance is in [references/evidence-templates.md](references/evidence-templates.md).

## Mandatory Checks

The two checks must both pass:

1. Unauthorized samples in manifest must be `0`.
2. Desensitization coverage must be exactly `100%`.

This skill includes an automated check script that computes:
- `unauthorized_count`
- `sensitive_fields_total`
- `masked_fields_pass`
- `coverage_percent`

It can also write summary results into:
- `docs/status/1.1-access-gate-check.md`
- `docs/status/1.1-desensitization-sampling-report.md`

## Backfill Status (Step 3)

After checks pass, update:

1. `openspec/changes/add-m1-week2-week3-task-plan/tasks.md`
- Change task `1.1` from `- [ ]` to `- [x]`.
- Add completion note with evidence links:
  - `docs/status/1.1-data-authorization-register.csv`
  - `docs/status/1.1-access-gate-check.md`
  - `docs/status/1.1-desensitization-rules-v1.md`
  - `docs/status/1.1-desensitization-sampling-report.md`

2. `docs/status/m1-week2-week3-execution-board.md`
- Change task `1.1` status from `In Progress` to `Completed`.

## Acceptance Checklist

- [ ] Four evidence files exist under `docs/status/`
- [ ] `unauthorized_count = 0`
- [ ] `coverage_percent = 100`
- [ ] Task `1.1` checked in `tasks.md` with evidence links
- [ ] Execution board task `1.1` status set to `Completed`

If any check fails, do not mark task `1.1` as completed.
