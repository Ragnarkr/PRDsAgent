param(
    [string]$RepoRoot = (Get-Location).Path,
    [switch]$Force
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Ensure-File {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Content
    )

    if ((Test-Path $Path) -and -not $Force) {
        Write-Host "[skip] $Path already exists"
        return
    }

    $dir = Split-Path -Parent $Path
    if ($dir -and -not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }

    Set-Content -Path $Path -Value $Content -Encoding UTF8
    Write-Host "[ok] wrote $Path"
}

$statusDir = Join-Path $RepoRoot "docs/status"
if (-not (Test-Path $statusDir)) {
    throw "Expected directory not found: $statusDir"
}

$authCsv = @"
sample_id,source,grant_scope,grantor,granted_at,expires_at,status,evidence_link
"@

$accessGate = @"
# 1.1 Access Gate Check

- Dataset version:
- Executed at:
- Manifest path:
- Unauthorized sample count:
- Result: PASS/FAIL
- Interception log link:
"@

$rulesDoc = @"
# 1.1 Desensitization Rules v1

- Rule version: v1
- Updated at:

## Sensitive Fields
- field_name:

## Rule Mapping
- field_name -> masking rule

## Before/After Examples
- before:
- after:
"@

$samplingReport = @"
# 1.1 Desensitization Sampling Report

- Executed at:
- Sample count:
- Sensitive fields total:
- Masked fields pass:
- Coverage:
- Result: PASS/FAIL
"@

Ensure-File -Path (Join-Path $statusDir "1.1-data-authorization-register.csv") -Content $authCsv
Ensure-File -Path (Join-Path $statusDir "1.1-access-gate-check.md") -Content $accessGate
Ensure-File -Path (Join-Path $statusDir "1.1-desensitization-rules-v1.md") -Content $rulesDoc
Ensure-File -Path (Join-Path $statusDir "1.1-desensitization-sampling-report.md") -Content $samplingReport
