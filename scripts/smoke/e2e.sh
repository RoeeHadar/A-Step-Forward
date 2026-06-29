#!/usr/bin/env bash
# Post-deploy smoke test. Runs against a deployed (staging or prod) environment.
#
# Usage:
#   WEB_BASE_URL=https://a-step-forward-waij.vercel.app \
#   API_BASE_URL=https://asf-api.fly.dev \
#     scripts/smoke/e2e.sh
#
# Exit non-zero on any failure. Designed to be invoked from deploy-prod.yml after
# the deploy job completes and from the Release Captain on demand.

set -euo pipefail

WEB_BASE_URL="${WEB_BASE_URL:?WEB_BASE_URL required}"
API_BASE_URL="${API_BASE_URL:?API_BASE_URL required}"
TIMEOUT="${SMOKE_TIMEOUT:-15}"

red()   { printf "\033[31m%s\033[0m\n" "$*"; }
green() { printf "\033[32m%s\033[0m\n" "$*"; }
say()   { printf "  • %s\n" "$*"; }

pass=0
fail=0
check() {
  local label="$1"; shift
  if "$@"; then
    green "[ok]    $label"; pass=$((pass+1))
  else
    red   "[fail]  $label"; fail=$((fail+1))
  fi
}

http_code() {
  curl -sS -o /dev/null -w "%{http_code}" --max-time "$TIMEOUT" "$1"
}

is_200() { [ "$(http_code "$1")" = "200" ]; }

say "Smoke target: web=$WEB_BASE_URL api=$API_BASE_URL"

check "web /                       200" is_200 "$WEB_BASE_URL/"
check "web /sign-in                200" is_200 "$WEB_BASE_URL/sign-in"
check "web /sign-up                200" is_200 "$WEB_BASE_URL/sign-up"
check "web /api/health             200" is_200 "$WEB_BASE_URL/api/health"

check "api /healthz                200" is_200 "$API_BASE_URL/healthz"
check "api /readyz                 200" is_200 "$API_BASE_URL/readyz"

# Lightweight content checks (no auth needed)
check "web / contains brand"      bash -c "curl -sS --max-time $TIMEOUT $WEB_BASE_URL/ | grep -qi 'A Step Forward'"
check "web / has noindex robots disabled" bash -c "curl -sS --max-time $TIMEOUT $WEB_BASE_URL/robots.txt | grep -qi 'allow'"

echo
echo "  pass=$pass  fail=$fail"
if [ "$fail" -gt 0 ]; then
  red "SMOKE FAILED"
  exit 1
fi
green "SMOKE OK"
