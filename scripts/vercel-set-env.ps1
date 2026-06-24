<#
.SYNOPSIS
  One-shot helper to point the Vercel-hosted frontend at the live Render backend.

.DESCRIPTION
  The Vercel CLI tends to hang on networks with TLS inspection, so this script
  drives the Vercel REST API directly. It looks up the project id, sets
  NEXT_PUBLIC_API_BASE_URL on Production + Preview, and triggers a redeploy via
  an empty git commit on `main`.

.PARAMETER Token
  Vercel personal access token. If omitted, falls back to $env:VERCEL_TOKEN.
  Token can be created at: https://vercel.com/account/tokens
  The same value is mirrored in GitHub Actions as the `VERCEL_TOKEN` secret.

.PARAMETER ProjectName
  Vercel project name. Defaults to "a-step-forward-waij".

.PARAMETER ApiBaseUrl
  Backend URL the frontend should call. Defaults to "https://asf-api.onrender.com".

.PARAMETER TeamSlug
  Optional Vercel team slug (e.g. "a-step-forward"). If omitted the script
  searches the personal scope first, then iterates teams.

.PARAMETER SkipRedeploy
  Don't create the empty commit / push at the end.

.EXAMPLE
  pwsh ./scripts/vercel-set-env.ps1 -Token "vercel_xxx"

.EXAMPLE
  $env:VERCEL_TOKEN = "vercel_xxx"
  pwsh ./scripts/vercel-set-env.ps1
#>
[CmdletBinding()]
param(
  [string]$Token = $env:VERCEL_TOKEN,
  [string]$ProjectName = "a-step-forward-waij",
  [string]$ApiBaseUrl = "https://asf-api-q566.onrender.com",
  [string]$TeamSlug = "",
  [switch]$SkipRedeploy
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($Token)) {
  Write-Error @"
Vercel token not provided.

Get one from https://vercel.com/account/tokens (or copy the value of the
`VERCEL_TOKEN` GitHub Actions secret), then re-run as:

  `$env:VERCEL_TOKEN = '<token>'
  pwsh ./scripts/vercel-set-env.ps1
"@
}

$headers = @{
  Authorization  = "Bearer $Token"
  "Content-Type" = "application/json"
}

function Invoke-Vercel {
  param([string]$Path, [string]$Method = "GET", [object]$Body)
  $uri = "https://api.vercel.com$Path"
  if ($Body) {
    return Invoke-RestMethod -Method $Method -Uri $uri -Headers $headers `
      -Body ($Body | ConvertTo-Json -Depth 6)
  }
  return Invoke-RestMethod -Method $Method -Uri $uri -Headers $headers
}

Write-Host "==> Resolving project '$ProjectName'..." -ForegroundColor Cyan

# Build candidate scopes: explicit team slug, then personal, then every team the token can see.
$scopes = New-Object System.Collections.Generic.List[object]
if ($TeamSlug) {
  $scopes.Add(@{ Label = "team:$TeamSlug"; Suffix = "?slug=$TeamSlug" })
}
$scopes.Add(@{ Label = "personal"; Suffix = "" })
try {
  $teams = Invoke-Vercel -Path "/v2/teams"
  foreach ($t in $teams.teams) {
    if ($TeamSlug -and $t.slug -eq $TeamSlug) { continue }
    $scopes.Add(@{ Label = "team:$($t.slug)"; Suffix = "?teamId=$($t.id)" })
  }
} catch {
  Write-Warning "Could not list teams ($($_.Exception.Message)); continuing with personal scope only."
}

$projectId = $null
$resolvedSuffix = $null
foreach ($scope in $scopes) {
  try {
    $resp = Invoke-Vercel -Path "/v9/projects/$ProjectName$($scope.Suffix)"
    if ($resp.id) {
      $projectId = $resp.id
      $resolvedSuffix = $scope.Suffix
      Write-Host "    found in $($scope.Label) -> id=$projectId" -ForegroundColor Green
      break
    }
  } catch {
    # try next scope
  }
}

if (-not $projectId) {
  Write-Error "Could not find Vercel project '$ProjectName' in any accessible scope. Re-run with -TeamSlug <slug>."
}

Write-Host "==> Listing existing env vars..." -ForegroundColor Cyan
$existing = Invoke-Vercel -Path "/v9/projects/$projectId/env$resolvedSuffix"
$matches = $existing.envs | Where-Object { $_.key -eq "NEXT_PUBLIC_API_BASE_URL" }

foreach ($m in $matches) {
  Write-Host "    deleting prior env id=$($m.id) target=$($m.target -join ',')"
  $delSuffix = if ($resolvedSuffix) { $resolvedSuffix } else { "" }
  Invoke-Vercel -Path "/v9/projects/$projectId/env/$($m.id)$delSuffix" -Method DELETE | Out-Null
}

Write-Host "==> Creating NEXT_PUBLIC_API_BASE_URL = $ApiBaseUrl (production+preview)" -ForegroundColor Cyan
$body = @{
  key    = "NEXT_PUBLIC_API_BASE_URL"
  value  = $ApiBaseUrl
  target = @("production", "preview")
  type   = "plain"
}
Invoke-Vercel -Path "/v10/projects/$projectId/env$resolvedSuffix" -Method POST -Body $body | Out-Null
Write-Host "    ok" -ForegroundColor Green

if ($SkipRedeploy) {
  Write-Host "==> Skipping redeploy (per -SkipRedeploy)." -ForegroundColor Yellow
  return
}

Write-Host "==> Triggering redeploy via empty commit on main..." -ForegroundColor Cyan
$current = (& git rev-parse --abbrev-ref HEAD).Trim()
if ($current -ne "main") {
  & git checkout main
}
& git pull --ff-only origin main
& git commit --allow-empty -m "chore(frontend): trigger Vercel redeploy for NEXT_PUBLIC_API_BASE_URL"
& git push origin main
Write-Host "    pushed; Vercel will redeploy in ~30s." -ForegroundColor Green
