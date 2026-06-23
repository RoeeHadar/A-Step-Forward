# Re-apply uv workspace sources when path-based entries creep back in (e.g. OneDrive sync).
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root
$files = Get-ChildItem -Recurse -Filter pyproject.toml | Where-Object { $_.FullName -notmatch '\\\.venv\\' }
foreach ($f in $files) {
  $c = Get-Content $f.FullName -Raw
  $orig = $c
  $c = $c -replace 'schemas = \{ path = "\.\./schemas", editable = true \}', 'schemas = { workspace = true }'
  $c = $c -replace 'schemas = \{ path = "\.\./\.\./packages/schemas", editable = true \}', 'schemas = { workspace = true }'
  $c = $c -replace 'memory-service = \{ path = "\.\./\.\./services/memory", editable = true \}', 'memory-service = { workspace = true }'
  $c = $c -replace 'memory-service = \{ path = "\.\./memory", editable = true \}', 'memory-service = { workspace = true }'
  $c = $c -replace 'curriculum-service = \{ path = "\.\./\.\./services/curriculum", editable = true \}', 'curriculum-service = { workspace = true }'
  $c = $c -replace 'graphrag-service = \{ path = "\.\./\.\./services/graphrag", editable = true \}', 'graphrag-service = { workspace = true }'
  $c = $c -replace 'graphrag-service = \{ path = "\.\./graphrag", editable = true \}', 'graphrag-service = { workspace = true }'
  $c = $c -replace 'agents = \{ path = "\.\./\.\./packages/agents", editable = true \}', 'agents = { workspace = true }'
  $c = $c -replace 'orchestrator = \{ path = "\.\./\.\./services/orchestrator", editable = true \}', 'orchestrator = { workspace = true }'
  if ($c -ne $orig) {
    Set-Content -Path $f.FullName -Value $c -NoNewline
    Write-Output "updated $($f.FullName)"
  }
}
