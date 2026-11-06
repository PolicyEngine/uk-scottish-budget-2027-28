#!/usr/bin/env bash
# Check a served build of the dashboard (scaled down from the Autumn Budget
# repo's script): every tab answers 200 under the base path, the page
# carries the robots noindex meta and the X-Robots-Tag header, the banner is
# on the page, and results.json is served.
#
# Usage: scripts/smoke-built-site.sh [site URL] [banner prefix]
#   default http://127.0.0.1:3000/uk/scottish-budget-2027-28
#   banner prefix: text the banner must start with (MOCK for a drill build)
set -euo pipefail

SITE="${1:-http://127.0.0.1:3000/uk/scottish-budget-2027-28}"
SITE="${SITE%/}"
BANNER_PREFIX="${2:-}"
TABS=("" "?tab=household" "?tab=policies" "?tab=methodology")

failures=0
body=$(mktemp)
headers=$(mktemp)
trap 'rm -f "$body" "$headers"' EXIT

fetch() {
  curl --silent --show-error --dump-header "$headers" --output "$body" \
    --write-out '%{http_code}' --max-time 60 "$1" || echo "000"
}

for tab in "${TABS[@]}"; do
  url="$SITE$tab"
  code=$(fetch "$url")
  if [ "$code" != 200 ]; then
    echo "FAIL $url: HTTP $code"
    failures=$((failures + 1))
    continue
  fi
  meta=$(grep -o '<meta name="robots"[^>]*>' "$body" || true)
  if ! printf '%s' "$meta" | grep -q noindex || ! printf '%s' "$meta" | grep -q nofollow; then
    echo "FAIL $url: robots meta is not noindex, nofollow ($meta)"
    failures=$((failures + 1))
  fi
  if ! grep -qi '^x-robots-tag:.*noindex' "$headers"; then
    echo "FAIL $url: no X-Robots-Tag noindex header"
    failures=$((failures + 1))
  fi
  if ! grep -q 'data-testid="pre-release-banner"' "$body"; then
    echo "FAIL $url: the banner is missing"
    failures=$((failures + 1))
  elif [ -n "$BANNER_PREFIX" ] && ! grep -q "data-testid=\"pre-release-banner\"[^>]*>$BANNER_PREFIX" "$body"; then
    echo "FAIL $url: the banner does not start with $BANNER_PREFIX"
    failures=$((failures + 1))
  fi
  echo "ok   $url"
done

code=$(fetch "$SITE/data/results.json")
if [ "$code" != 200 ] || [ ! -s "$body" ]; then
  echo "FAIL $SITE/data/results.json: HTTP $code"
  failures=$((failures + 1))
else
  echo "ok   $SITE/data/results.json"
fi

if [ "$failures" -gt 0 ]; then
  echo "$failures check(s) failed"
  exit 1
fi
echo "All checks passed"
