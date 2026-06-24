<#
.SYNOPSIS
  Wire live Render + Clerk credentials on Vercel (Production + Preview).

.DESCRIPTION
  Sets NEXT_PUBLIC_API_BASE_URL, NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY, and
  CLERK_SECRET_KEY via the Vercel REST API. Render env vars (GROQ_API_KEY,
  CLERK_JWKS_URL, CLERK_ISSUER) must still be pasted in the Render dashboard —
  see BLOCKED.md §5d.

  Prefer the GitHub Actions workflow `.github/workflows/wire-vercel-env.yml`
  when VERCEL_TOKEN is only available as a GitHub secret.

.PARAMETER VercelToken
  Vercel personal access token. Defaults to $env:VERCEL_TOKEN.

.PARAMETER ProjectId
  Defaults to the a-step-forward-waij project id.

.PARAMETER TeamId
  Vercel team id (org). Defaults to team_hHUHxwd68CG96Qq2VC4d2dqN.

.PARAMETER ApiBaseUrl
  Render backend URL. Defaults to https://asf-api-q566.onrender.com.

.PARAMETER ClerkPublishableKey
  NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY value.

.PARAMETER ClerkSecretKey
  CLERK_SECRET_KEY value.

.PARAMETER SkipRedeploy
  Do not create an empty commit on main.

.EXAMPLE
  pwsh ./scripts/wire-env-vars.ps1 `
    -VercelToken $env:VERCEL_TOKEN `
    -ClerkPublishableKey "pk_test_..." `
    -ClerkSecretKey "sk_test_..."
#>
[CmdletBinding()]
param(
  [string]$VercelToken = $env:VERCEL_TOKEN,
  [string]$ProjectId = "prj_umQ9fPzv8CKX9Enh7yN0V7mpUfTA",
  [string]$TeamId = "team_hHUHxwd68CG96Qq2VC4d2dqN",
  [string]$ApiBaseUrl = "https://asf-api-q566.onrender.com",
  [Parameter(Mandatory = $true)]
  [string]$ClerkPublishableKey,
  [Parameter(Mandatory = $true)]
  [string]$ClerkSecretKey,
  [switch]$SkipRedeploy
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($VercelToken)) {
  Write-Error "Vercel token required. Pass -VercelToken or set `$env:VERCEL_TOKEN. Or run: gh workflow run wire-vercel-env.yml"
}

$headers = @{
  Authorization  = "Bearer $VercelToken"
  "Content-Type" = "application/json"
}
$scope = "?teamId=$TeamId"

function Invoke-Vercel {
  param([string]$Path, [string]$Method = "GET", [object]$Body)
  $uri = "https://api.vercel.com$Path$scope"
  if ($Body) {
    return Invoke-RestMethod -Method $Method -Uri $uri -Headers $headers `
      -Body ($Body | ConvertTo-Json -Depth 6)
  }
  return Invoke-RestMethod -Method $Method -Uri $uri -Headers $headers
}

function Set-VercelEnv {
  param([string]$Key, [string]$Value)
  $existing = Invoke-Vercel -Path "/v9/projects/$ProjectId/env"
  foreach ($m in ($existing.envs | Where-Object { $_.key -eq $Key })) {
    Write-Host "  deleting prior $Key (id=$($m.id))"
    Invoke-Vercel -Path "/v9/projects/$ProjectId/env/$($m.id)" -Method DELETE | Out-Null
  }
  $body = @{
    key    = $Key
    value  = $Value
    target = @("production", "preview")
    type   = "plain"
  }
  Invoke-Vercel -Path "/v10/projects/$ProjectId/env" -Method POST -Body $body | Out-Null
  Write-Host "  set $Key" -ForegroundColor Green
}

Write-Host "==> Wiring Vercel env (project=$ProjectId)" -ForegroundColor Cyan
Set-VercelEnv -Key "NEXT_PUBLIC_API_BASE_URL" -Value $ApiBaseUrl
Set-VercelEnv -Key "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY" -Value $ClerkPublishableKey
Set-VercelEnv -Key "CLERK_SECRET_KEY" -Value $ClerkSecretKey
Write-Host "==> Done. Render vars still required — see BLOCKED.md §5d" -ForegroundColor Yellow

if ($SkipRedeploy) { return }

Write-Host "==> Triggering redeploy via empty commit on main..." -ForegroundColor Cyan
$current = (& git rev-parse --abbrev-ref HEAD).Trim()
if ($current -ne "main") { & git checkout main }
& git pull --ff-only origin main
& git commit --allow-empty -m "chore(frontend): pick up live API + Clerk env vars"
& git push origin main
