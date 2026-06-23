#requires -Version 5.1
<#
.SYNOPSIS
  Post-deploy smoke test, PowerShell mirror of scripts/smoke/e2e.sh.

.EXAMPLE
  $env:WEB_BASE_URL = 'https://a-step-forward.vercel.app'
  $env:API_BASE_URL = 'https://asf-api.fly.dev'
  .\scripts\smoke\e2e.ps1
#>

[CmdletBinding()]
param(
  [string]$WebBaseUrl = $env:WEB_BASE_URL,
  [string]$ApiBaseUrl = $env:API_BASE_URL,
  [int]$TimeoutSec   = [int]($env:SMOKE_TIMEOUT ?? 15)
)

if (-not $WebBaseUrl) { throw 'WEB_BASE_URL required' }
if (-not $ApiBaseUrl) { throw 'API_BASE_URL required' }

$pass = 0; $fail = 0
function Pass($m) { Write-Host "[ok]   $m" -ForegroundColor Green; $script:pass++ }
function Fail($m) { Write-Host "[fail] $m" -ForegroundColor Red; $script:fail++ }

function Test-Http200($url, $label) {
  try {
    $r = Invoke-WebRequest -Uri $url -Method Head -TimeoutSec $TimeoutSec -ErrorAction Stop -SkipHttpErrorCheck
    if ($r.StatusCode -eq 200) { Pass $label } else { Fail "$label (status=$($r.StatusCode))" }
  } catch { Fail "$label ($_)" }
}

function Test-Contains($url, $needle, $label) {
  try {
    $r = Invoke-WebRequest -Uri $url -TimeoutSec $TimeoutSec -ErrorAction Stop
    if ($r.Content -match [regex]::Escape($needle)) { Pass $label } else { Fail "$label (missing '$needle')" }
  } catch { Fail "$label ($_)" }
}

Write-Host "Smoke target: web=$WebBaseUrl  api=$ApiBaseUrl"

Test-Http200 "$WebBaseUrl/"                'web /'
Test-Http200 "$WebBaseUrl/sign-in"         'web /sign-in'
Test-Http200 "$WebBaseUrl/sign-up"         'web /sign-up'
Test-Http200 "$WebBaseUrl/api/health"      'web /api/health'

Test-Http200 "$ApiBaseUrl/healthz"         'api /healthz'
Test-Http200 "$ApiBaseUrl/readyz"          'api /readyz'

Test-Contains "$WebBaseUrl/"               'A Step Forward' 'web / contains brand'

Write-Host ""
Write-Host "  pass=$pass  fail=$fail"
if ($fail -gt 0) { Write-Host 'SMOKE FAILED' -ForegroundColor Red; exit 1 }
Write-Host 'SMOKE OK' -ForegroundColor Green
