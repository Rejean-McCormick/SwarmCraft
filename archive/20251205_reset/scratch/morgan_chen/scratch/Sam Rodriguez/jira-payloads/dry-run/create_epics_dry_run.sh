#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
EPICS_DIR="$SCRIPT_DIR/../epics"
DRY_LOG="$SCRIPT_DIR/dry_run_log.json"

if [[ ! -d "$EPICS_DIR" ]]; then
  echo "Epics directory not found: $EPICS_DIR" >&2
  exit 1
fi

# Start log
printf "[" > "$DRY_LOG"
first=1
for f in "$EPICS_DIR"/*.json; do
  [[ -e "$f" ]] || continue
  epic_name="$(basename "$f" .json)"
  if [[ $first -eq 0 ]]; then
    printf "," >> "$DRY_LOG"
  else
    first=0
  fi
  printf '{"epic_file":"%s","epic_name":"%s","status":"dry-run","payload_file":"%s"}' "$f" "$epic_name" "$f" >> "$DRY_LOG"
  echo "Simulating epic: $epic_name (payload: $f)"
done
printf "]\n" >> "$DRY_LOG"
echo "Dry-run complete. Log saved to $DRY_LOG" 
