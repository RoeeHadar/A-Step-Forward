# Install Obsidian MCP into Cursor global config (%USERPROFILE%\.cursor\mcp.json)
# Run from repo root:
#   powershell -ExecutionPolicy Bypass -File scripts/install-cursor-obsidian-mcp.ps1
#
# Uses node + .mjs with separate argv (NOT cmd /c + unquoted .cmd path).
# Paths with spaces (e.g. "A Step Forward") break when passed to cmd /c without quotes.

$ErrorActionPreference = 'Stop'

$repo = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$launcher = Join-Path $repo 'scripts\mcp-obsidian-vault.mjs'
$cursorDir = Join-Path $env:USERPROFILE '.cursor'
$mcpPath = Join-Path $cursorDir 'mcp.json'
$serverName = 'asf-obsidian'

if (-not (Test-Path $launcher)) {
  Write-Error "Launcher not found: $launcher"
}

$nodeCmd = $null
$pf = $env:ProgramFiles
$pf86 = ${env:ProgramFiles(x86)}
foreach ($candidate in @(
  (Join-Path $pf 'nodejs\node.exe'),
  (Join-Path $pf86 'nodejs\node.exe'),
  'node'
)) {
  if ($candidate -eq 'node') {
    $nodeCmd = 'node'
    break
  }
  if ($candidate -and (Test-Path $candidate)) {
    $nodeCmd = $candidate
    break
  }
}

if (-not $nodeCmd) {
  Write-Error 'node.exe not found. Install Node.js or ensure node is on PATH.'
}

if (-not (Test-Path $cursorDir)) {
  New-Item -ItemType Directory -Path $cursorDir | Out-Null
}

# Separate argv entries: no cmd.exe re-tokenization, so spaces in $launcher are safe.
$entry = @{
  command = $nodeCmd
  args    = @($launcher)
}

if (Test-Path $mcpPath) {
  $raw = Get-Content $mcpPath -Raw -Encoding UTF8
  try {
    $config = $raw | ConvertFrom-Json
  } catch {
    Write-Error "Invalid JSON in $mcpPath - fix or rename it, then re-run."
  }
  if (-not $config.mcpServers) {
    $config | Add-Member -NotePropertyName mcpServers -NotePropertyValue ([pscustomobject]@{})
  }
  $config.mcpServers | Add-Member -NotePropertyName $serverName -NotePropertyValue $entry -Force
  $config | ConvertTo-Json -Depth 6 | Set-Content -Path $mcpPath -Encoding UTF8
} else {
  $config = [ordered]@{
    mcpServers = [ordered]@{
      $serverName = $entry
    }
  }
  ($config | ConvertTo-Json -Depth 6) | Set-Content -Path $mcpPath -Encoding UTF8
}

Write-Host "Installed '$serverName' -> $mcpPath"
Write-Host "  command: $nodeCmd"
Write-Host "  args[0]: $launcher"
Write-Host 'Next:'
Write-Host '  1. Quit Cursor completely (File -> Exit)'
Write-Host '  2. Reopen this repo'
Write-Host "  3. Ctrl+Shift+J -> Tools and MCP -> enable '$serverName'"
Write-Host 'See obsidian-vault/MCP-ENABLE.md for details.'
