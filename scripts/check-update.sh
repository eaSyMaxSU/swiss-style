#!/usr/bin/env bash
# Once a day, compare VERSION with the latest GitHub release.
# Sends no document or task content. Silent when offline or already checked.
set -u
marker="${XDG_CACHE_HOME:-$HOME/.cache}/swiss-style/update-check"
mkdir -p "$(dirname "$marker")" 2>/dev/null || exit 0
if [[ -f "$marker" ]]; then
  now=$(date +%s)
  if [[ "$(uname)" == "Darwin" ]]; then
    then=$(stat -f %m "$marker" 2>/dev/null || echo 0)
  else
    then=$(stat -c %Y "$marker" 2>/dev/null || echo 0)
  fi
  if (( now - then < 86400 )); then
    exit 0
  fi
fi
touch "$marker" 2>/dev/null || true
root=$(cd "$(dirname "$0")/.." && pwd)
local_ver=$(cat "$root/VERSION" 2>/dev/null || exit 0)
remote=$(curl -fsS --max-time 3 https://api.github.com/repos/eaSyMaxSU/swiss-style/releases/latest 2>/dev/null || true)
tag=$(printf '%s' "$remote" | sed -n 's/.*"tag_name":[[:space:]]*"\([^"]*\)".*/\1/p' | head -n 1)
tag=${tag#v}
if [[ -n "${tag}" && "${tag}" != "${local_ver}" ]]; then
  printf 'Swiss Style %s is available (this copy is %s).\n' "$tag" "$local_ver"
fi
exit 0
