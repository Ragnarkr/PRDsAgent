param(
    [string]$RepoRoot = (Get-Location).Path,
    [switch]$WriteReports
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Require-File {
    param([Parameter(Mandatory = $true)][string]$Path)
    if (-not (Test-Path $Path)) {
        throw "Required file not found: $Path"
    }
}

function Get-ManifestSampleIds {
    param([Parameter(Mandatory = $true)][string]$Path)

    $sampleIds = @()
    foreach ($line in Get-Content $Path) {
        if ([string]::IsNullOrWhiteSpace($line)) {
            continue
        }

        $item = $line | ConvertFrom-Json
        if (-not $item.sample_id) {
            throw "Manifest row missing sample_id: $line"
        }
        $sampleIds += [string]$item.sample_id
    }
    return $sampleIds
}

function Write-AccessGateReport {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$ExecutedAt,
        [Parameter(Mandatory = $true)][string]$ManifestPath,
        [Parameter(Mandatory = $true)][int]$UnauthorizedCount
    )

    $result = if ($UnauthorizedCount -eq 0) { "PASS" } else { "FAIL" }
    $body = @"
# 1.1 Access Gate Check

- Dataset version: dataset-m1-v1
- Executed at: $ExecutedAt
- Manifest path: $ManifestPath
- Unauthorized sample count: $UnauthorizedCount
- Result: $result
- Interception log link: TODO
"@
    Set-Content -Path $Path -Value $body -Encoding UTF8
}

function Write-SamplingReport {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$ExecutedAt,
        [Parameter(Mandatory = $true)][int]$SampleCount,
        [Parameter(Mandatory = $true)][double]$SensitiveTotal,
        [Parameter(Mandatory = $true)][double]$MaskedPass,
        [Parameter(Mandatory = $true)][double]$CoveragePercent
    )

    $result = if ($SensitiveTotal -gt 0 -and $CoveragePercent -eq 100.0) { "PASS" } else { "FAIL" }
    $body = @"
# 1.1 Desensitization Sampling Report

- Executed at: $ExecutedAt
- Sample count: $SampleCount
- Sensitive fields total: $SensitiveTotal
- Masked fields pass: $MaskedPass
- Coverage: $CoveragePercent%
- Result: $result
"@
    Set-Content -Path $Path -Value $body -Encoding UTF8
}

$manifestPath = Join-Path $RepoRoot "dataset-m1-v1/manifest.jsonl"
$authCsvPath = Join-Path $RepoRoot "docs/status/1.1-data-authorization-register.csv"
$sampleCheckPath = Join-Path $RepoRoot "docs/status/1.1-desensitization-sample-check.csv"
$accessGateReportPath = Join-Path $RepoRoot "docs/status/1.1-access-gate-check.md"
$samplingReportPath = Join-Path $RepoRoot "docs/status/1.1-desensitization-sampling-report.md"

Require-File -Path $manifestPath
Require-File -Path $authCsvPath
Require-File -Path $sampleCheckPath

$manifest = Get-ManifestSampleIds -Path $manifestPath
$approved = Import-Csv $authCsvPath |
    Where-Object { $_.status -eq "approved" } |
    ForEach-Object { [string]$_.sample_id }

$unauthorizedCount = (
    Compare-Object $manifest $approved |
    Where-Object { $_.SideIndicator -eq "<=" }
).Count

$sampleRows = Import-Csv $sampleCheckPath
$sampleCount = @($sampleRows).Count
$sensitiveFieldsTotal = [double](($sampleRows | Measure-Object -Property sensitive_fields_total -Sum).Sum)
$maskedFieldsPass = [double](($sampleRows | Measure-Object -Property masked_fields_pass -Sum).Sum)

if ($sensitiveFieldsTotal -eq 0) {
    $coveragePercent = 0.0
}
else {
    $coveragePercent = [Math]::Round(($maskedFieldsPass / $sensitiveFieldsTotal) * 100, 2)
}

$authorizedPass = ($unauthorizedCount -eq 0)
$coveragePass = ($sensitiveFieldsTotal -gt 0 -and $coveragePercent -eq 100.0)

$executedAt = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss K")

if ($WriteReports) {
    Write-AccessGateReport `
        -Path $accessGateReportPath `
        -ExecutedAt $executedAt `
        -ManifestPath $manifestPath `
        -UnauthorizedCount $unauthorizedCount

    Write-SamplingReport `
        -Path $samplingReportPath `
        -ExecutedAt $executedAt `
        -SampleCount $sampleCount `
        -SensitiveTotal $sensitiveFieldsTotal `
        -MaskedPass $maskedFieldsPass `
        -CoveragePercent $coveragePercent
}

$summary = [PSCustomObject]@{
    unauthorized_count      = $unauthorizedCount
    authorization_pass      = $authorizedPass
    sample_count            = $sampleCount
    sensitive_fields_total  = $sensitiveFieldsTotal
    masked_fields_pass      = $maskedFieldsPass
    coverage_percent        = $coveragePercent
    coverage_pass           = $coveragePass
    write_reports           = [bool]$WriteReports
}

$summary | ConvertTo-Json -Depth 4

if (-not $authorizedPass -or -not $coveragePass) {
    throw "Validation failed: unauthorized_count must be 0 and coverage_percent must be 100."
}
