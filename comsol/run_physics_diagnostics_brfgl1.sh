#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
COMSOL_BIN="/Applications/COMSOL60/Multiphysics/bin/comsol"
DIAG_JAVA="$PROJECT_DIR/comsol/run_physics_diagnostics_brfgl1.java"
DIAG_CLASS="$PROJECT_DIR/comsol/run_physics_diagnostics_brfgl1.class"
LOG_DIR="$PROJECT_DIR/results/raw_comsol_exports/PHYSICS_DIAGNOSTICS_RUN003"

mkdir -p "$LOG_DIR"
export BRFGL1_PROJECT_ROOT="$PROJECT_DIR"

"$COMSOL_BIN" compile "$DIAG_JAVA" 2>&1 | tee "$LOG_DIR/compile.log"
"$COMSOL_BIN" batch \
  -autosave off \
  -inputfile "$DIAG_CLASS" \
  -batchlog "$LOG_DIR/diagnostics_batch.log" \
  -batchlogout 2>&1 | tee "$LOG_DIR/diagnostics_stdout.log"
