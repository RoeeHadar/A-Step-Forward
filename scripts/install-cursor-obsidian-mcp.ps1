# Install Obsidian MCP into Cursor global config (%USERPROFILE%\.cursor\mcp.json)
# Run from repo root:
#   powershell -ExecutionPolicy Bypass -File scripts/install-cursor-obsidian-mcp.ps1

$ErrorActionPreference = 'Stop'

$repo = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$launcher = Join-Path $repo 'scripts\mcp-obsidian-vault.cmd'
$cursorDir = Join-Path $env:USERPROFILE '.cursor'
$mcpPath = Join-Path $cursorDir 'mcp.json'
$serverName = 'asf-obsidian'

if (-not (Test-Path $launcher)) {
  Write-Error "Launcher not found: $launcher"
}

if (-not (Test-Path $cursorDir)) {
  New-Item -ItemType Directory -Path $cursorDir | Out-Null
}

$entry = @{
  command = 'cmd'
  args    = @('/c', $launcher)
}

if (Test-Path $mcpPath) {
  $raw = Get-Content $mcpPath -Raw -Encoding UTF8
  try {
    $config = $raw | ConvertFrom-Json
  } catch {
    Write-Error "Invalid JSON in $mcpPath — fix or rename it, then re-run."
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
Write-Host "Next:"
Write-Host "  1. Quit Cursor completely (File -> Exit)"
Write-Host "  2. Reopen this repo"
Write-Host "  3. Ctrl+Shift+J -> Tools & MCP -> enable '$serverName'"
Write-Host "See obsidian-vault/MCP-ENABLE.md for details."
