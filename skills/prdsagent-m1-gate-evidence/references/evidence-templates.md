# 1.1 Evidence Templates (PRDsAgent)

Use these templates when creating or repairing the minimum package files in `docs/status/`.

## 1) 1.1-data-authorization-register.csv

Required header:

```csv
sample_id,source,grant_scope,grantor,granted_at,expires_at,status,evidence_link
```

Status must use `approved` for rows allowed into evaluation.

## 2) 1.1-access-gate-check.md

Minimum sections:

```markdown
# 1.1 Access Gate Check

- Dataset version:
- Executed at:
- Manifest path:
- Unauthorized sample count:
- Result: PASS/FAIL
- Interception log link:
```

Rule: unauthorized sample count must equal `0`.

## 3) 1.1-desensitization-rules-v1.md

Minimum sections:

```markdown
# 1.1 Desensitization Rules v1

- Rule version:
- Updated at:

## Sensitive Fields
- field_name:

## Rule Mapping
- field_name -> masking rule

## Before/After Examples
- before:
- after:
```

## 4) 1.1-desensitization-sampling-report.md

Minimum sections:

```markdown
# 1.1 Desensitization Sampling Report

- Executed at:
- Sample count:
- Sensitive fields total:
- Masked fields pass:
- Coverage:
- Result: PASS/FAIL
```

Rule: coverage must equal `100%`.
