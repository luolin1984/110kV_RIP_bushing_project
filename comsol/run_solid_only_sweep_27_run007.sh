#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
COMSOL_BIN="/Applications/COMSOL60/Multiphysics/bin/comsol"
LOG_DIR="$PROJECT_DIR/results/raw_comsol_exports/SOLID_ONLY_SWEEP_27_RUN007"

mkdir -p "$LOG_DIR"
cd "$PROJECT_DIR"
export BRFGL1_PROJECT_ROOT="$PROJECT_DIR"

"$COMSOL_BIN" compile "$PROJECT_DIR/comsol/build_solid_only_physics_brfgl1.java" 2>&1 | tee "$LOG_DIR/compile_build_solid_only_physics.log"
"$COMSOL_BIN" batch \
  -autosave off \
  -inputfile "$PROJECT_DIR/comsol/build_solid_only_physics_brfgl1.class" \
  -outputfile "$PROJECT_DIR/comsol/BRFGL1-126-1250-4_solid_only_physics.mph" \
  -batchlog "$LOG_DIR/build_solid_only_physics_batch.log" \
  -batchlogout 2>&1 | tee "$LOG_DIR/build_solid_only_physics_stdout.log"

"$COMSOL_BIN" compile "$PROJECT_DIR/comsol/run_solid_only_sweep_27_run007.java" 2>&1 | tee "$LOG_DIR/compile_sweep.log"
"$COMSOL_BIN" batch \
  -autosave off \
  -inputfile "$PROJECT_DIR/comsol/run_solid_only_sweep_27_run007.class" \
  -batchlog "$LOG_DIR/sweep_batch.log" \
  -batchlogout 2>&1 | tee "$LOG_DIR/sweep_stdout.log"
