# Skill: pnpm-lockfile-ci

**Purpose**: Diagnose and fix recurring Vercel build failures caused by a stale
`pnpm-lock.yaml`, covering both main-branch commits and Dependabot PRs.

---

## When to use this skill

Use whenever you see any of these symptoms:

- Vercel build fails with `ERR_PNPM_OUTDATED_LOCKFILE`
- Vercel build fails with `Command "cd ../.. && pnpm install --frozen-lockfile" exited with 1`
- Vercel build fails with `Command "cd ../.. && pnpm --filter @asf/web build" exited with 1`
  immediately after the install step succeeds (possible UTF-8 / webpack issue)
- A Dependabot npm/yarn PR is failing CI

---

## Root cause catalogue

### A. Stale lockfile on a feature/fix branch

Someone edited `apps/web/package.json` (or another workspace `package.json`) and
committed without regenerating `pnpm-lock.yaml`.

**Fix**
```powershell
# From repo root
pnpm install          # regenerates lockfile
git add pnpm-lock.yaml
git commit -m "chore(deps): regenerate pnpm-lock.yaml"
git push
```

### B. Dependabot npm bump has stale lockfile

Dependabot only edits `package.json`; it cannot regenerate `pnpm-lock.yaml`.
The automated fix is `.github/workflows/dependabot-lockfile.yml`, which runs
`pnpm install --no-frozen-lockfile` and pushes the updated lockfile back to the
Dependabot branch on every Dependabot npm PR.

If that workflow isn't present or fails:

```bash
# Checkout the Dependabot branch locally and fix manually
git fetch origin
git checkout dependabot/npm_and_yarn/apps/web/<pkg>
pnpm install --no-frozen-lockfile
git add pnpm-lock.yaml
git commit -m "chore(deps): regenerate pnpm-lock.yaml"
git push
```

To close a batch of bad PRs in bulk:
```bash
gh pr list --author "app/dependabot" --state open \
  | awk '{print $1}' \
  | xargs -I{} gh pr close {} --comment "Stale lockfile — re-trigger with @dependabot recreate"
```

### C. Invalid UTF-8 bytes in a source file (webpack crash)

A source file was saved in Windows-1252 / Latin-1 encoding, leaving bytes
that are not valid UTF-8 (e.g. `0xB7` for `·`). webpack rejects the file:
`stream did not contain valid UTF-8`.

**Diagnosis**
```powershell
# Find all non-UTF-8 bytes in a file
$bytes = [System.IO.File]::ReadAllBytes("apps\web\src\app\layout.tsx")
$i = 0; $bad = @()
while ($i -lt $bytes.Length) {
    $b = $bytes[$i]
    if ($b -le 0x7F)                                                      { $i++;   continue }
    if ($b -ge 0xC2 -and $b -le 0xDF -and $bytes[$i+1] -ge 0x80)         { $i+=2;  continue }
    if ($b -ge 0xE0 -and $b -le 0xEF -and $bytes[$i+1] -ge 0x80)         { $i+=3;  continue }
    if ($b -ge 0xF0 -and $b -le 0xF4 -and $bytes[$i+1] -ge 0x80)         { $i+=4;  continue }
    $bad += "0x$("{0:X2}" -f $b) @ $i"; $i++
}
$bad
```

**Fix**
Replace the offending characters with Unicode escapes in the source file
(e.g. `·` → `\u00b7`, `–` → `\u2013`, `'` → `\u2019`) so the file is
unambiguously UTF-8 regardless of editor encoding settings.

Alternatively, ensure your editor and git are configured to use UTF-8:
```
# .editorconfig
[*.{ts,tsx,js,jsx}]
charset = utf-8
```

---

## Prevention checklist

- [ ] `.editorconfig` at repo root sets `charset = utf-8` for all TS/TSX/JS files.
- [ ] `.github/workflows/dependabot-lockfile.yml` exists and is enabled.
- [ ] CI (`lint-test.yml`) runs `pnpm install --frozen-lockfile` on every PR to
      catch stale lockfiles before merge.
- [ ] Never bump a package in `package.json` without running `pnpm install` locally
      and committing the updated `pnpm-lock.yaml` in the same commit.

---

## Files involved

| File | Role |
|------|------|
| `pnpm-lock.yaml` | Must be kept in sync with all workspace `package.json` files |
| `.github/workflows/dependabot-lockfile.yml` | Auto-regenerates lockfile on Dependabot PRs |
| `.editorconfig` | Enforces UTF-8 encoding for source files |
| `apps/web/src/app/layout.tsx` | Previously contained an invalid UTF-8 byte (`0xB7`) |
