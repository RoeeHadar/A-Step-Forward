# Verify GitHub Actions + Vercel deployment for a commit on main.
# Usage: .\scripts\verify-deploy.ps1 [-Sha HEAD] [-TimeoutMinutes 8]
param(
  [string]$Sha = "HEAD",
  [int]$TimeoutMinutes = 8
)

$ErrorActionPreference = "Stop"
$repo = "RoeeHadar/A-Step-Forward"
$resolvedSha = (git rev-parse $Sha).Trim()
$deadline = (Get-Date).AddMinutes($TimeoutMinutes)
$requiredWorkflows = @("Deploy Web (Vercel)", "Lint & Test")

Write-Host "Verifying deploy for $resolvedSha (timeout ${TimeoutMinutes}m)..."

function Wait-Workflows {
  while ((Get-Date) -lt $deadline) {
    $raw = gh run list --branch main --limit 20 --json databaseId,name,headSha,status,conclusion | ConvertFrom-Json
    $runs = @($raw | Where-Object { $_.headSha -eq $resolvedSha -and ($requiredWorkflows -contains $_.name) })

    $pending = @($runs | Where-Object { $_.status -ne "completed" })
    if ($pending.Count -eq 0 -and $runs.Count -ge $requiredWorkflows.Count) {
      return $runs
    }

    Write-Host ("  waiting... " + ($runs | ForEach-Object { "$($_.name)=$($_.status)" }) -join ", ")
    Start-Sleep -Seconds 20
  }
  throw "Timed out waiting for workflows on $resolvedSha"
}

$runs = Wait-Workflows
$failed = $runs | Where-Object { $_.conclusion -ne "success" }
if ($failed.Count -gt 0) {
  foreach ($f in $failed) {
    Write-Host "FAILED: $($f.name) (run $($f.databaseId))"
    gh run view $f.databaseId --log-failed 2>&1 | Select-Object -Last 30
  }
  exit 1
}

Write-Host "GitHub Actions: OK"

$deploymentJson = gh api "repos/$repo/deployments?sha=$resolvedSha&per_page=5"
$deployments = $deploymentJson | ConvertFrom-Json
if ($deployments -isnot [System.Array]) { $deployments = @($deployments) }
$deployment = $deployments | Select-Object -First 1
if (-not $deployment) {
  Write-Host "WARN: no GitHub deployment record for SHA (Vercel may still be building)"
} else {
  $statusJson = gh api $deployment.statuses_url
  $statuses = $statusJson | ConvertFrom-Json
  if ($statuses -isnot [System.Array]) { $statuses = @($statuses) }
  # API returns newest first; take the latest state's name only (not member-enumeration).
  $latestState = [string]$statuses[0].state
  Write-Host "Vercel deployment state: $latestState ($($deployment.environment))"
  if ($latestState -ne "success") {
    Write-Host ([string]$statuses[0].description)
    exit 1
  }
}

$urls = @("/", "/sign-in", "/learn")
foreach ($path in $urls) {
  $url = "https://a-step-forward-waij.vercel.app$path"
  try {
    $r = Invoke-WebRequest -Uri $url -UseBasicParsing -MaximumRedirection 5 -TimeoutSec 30
    Write-Host "  $($r.StatusCode) $path"
  } catch {
    Write-Host "  FAIL $path - $($_.Exception.Message)"
    exit 1
  }
}

Write-Host "Deploy verification passed."
