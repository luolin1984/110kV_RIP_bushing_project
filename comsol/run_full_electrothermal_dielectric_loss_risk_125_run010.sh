#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
COMSOL_BIN="/Applications/COMSOL60/Multiphysics/bin/comsol"
LOG_DIR="$PROJECT_DIR/results/raw_comsol_exports/FULL_ELECTROTHERMAL_DIELECTRIC_LOSS_RISK_125_RUN010"
PYTHON_BIN="/Users/luolin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"

mkdir -p "$LOG_DIR"
cd "$PROJECT_DIR"
export BRFGL1_PROJECT_ROOT="$PROJECT_DIR"

"$COMSOL_BIN" compile "$PROJECT_DIR/comsol/run_full_electrothermal_dielectric_loss_risk_125_run010.java" 2>&1 | tee "$LOG_DIR/compile_run010.log"
"$COMSOL_BIN" batch \
  -autosave off \
  -inputfile "$PROJECT_DIR/comsol/run_full_electrothermal_dielectric_loss_risk_125_run010.class" \
  -batchlog "$LOG_DIR/run010_batch.log" \
  -batchlogout 2>&1 | tee "$LOG_DIR/run010_stdout.log"

"$PYTHON_BIN" "$PROJECT_DIR/scripts/plot_full_electrothermal_risk_125_run010.py"
