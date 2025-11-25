#!/usr/bin/env bash
# automation/run_daily.sh
set -euo pipefail

# Resolve paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

VENV="$ROOT_DIR/.venv"
LOG_DIR="$ROOT_DIR/logs"

mkdir -p "$LOG_DIR"

TS="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
RUN_LOG="$LOG_DIR/run_${TS}.log"

# --- Activate virtualenv ---
if [[ -f "$VENV/bin/activate" ]]; then
  # shellcheck source=/dev/null
  source "$VENV/bin/activate"
else
  echo "[ERR] venv not found at $VENV" | tee -a "$RUN_LOG"
  exit 1
fi

# --- Load .env from automation/ ---
set -a
if [[ -f "$SCRIPT_DIR/.env" ]]; then
  # shellcheck source=/dev/null
  source "$SCRIPT_DIR/.env"
fi
set +a

# Default: stay in dry-run while testing
export DRY_RUN="${DRY_RUN:-true}"

echo "=== $TS | run_daily.sh start ===" | tee -a "$RUN_LOG"
echo "ROOT_DIR=$ROOT_DIR" | tee -a "$RUN_LOG"
echo "DRY_RUN=$DRY_RUN" | tee -a "$RUN_LOG"

echo "[INFO] Running python -m automation.main" | tee -a "$RUN_LOG"
python -m automation.main 2>&1 | tee -a "$RUN_LOG"

END_TS="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "=== $END_TS | run_daily.sh done ===" | tee -a "$RUN_LOG"