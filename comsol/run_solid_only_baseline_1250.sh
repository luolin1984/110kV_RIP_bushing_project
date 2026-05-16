#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
COMSOL_BIN="/Applications/COMSOL60/Multiphysics/bin/comsol"
LOG_DIR="$PROJECT_DIR/results/raw_comsol_exports/SOLID_ONLY_RUN004"

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

"$COMSOL_BIN" compile "$PROJECT_DIR/comsol/run_solid_only_baseline_1250.java" 2>&1 | tee "$LOG_DIR/compile_run_solid_only_baseline.log"
"$COMSOL_BIN" batch \
  -autosave off \
  -inputfile "$PROJECT_DIR/comsol/run_solid_only_baseline_1250.class" \
  -outputfile "$PROJECT_DIR/comsol/BRFGL1-126-1250-4_solid_only_baseline_RUN004.mph" \
  -batchlog "$LOG_DIR/run_solid_only_baseline_batch.log" \
  -batchlogout 2>&1 | tee "$LOG_DIR/run_solid_only_baseline_stdout.log"

"$COMSOL_BIN" compile "$PROJECT_DIR/comsol/export_solid_only_heat_balance.java" 2>&1 | tee "$LOG_DIR/compile_export_solid_only.log"
"$COMSOL_BIN" batch \
  -autosave off \
  -inputfile "$PROJECT_DIR/comsol/export_solid_only_heat_balance.class" \
  -batchlog "$LOG_DIR/export_solid_only_batch.log" \
  -batchlogout 2>&1 | tee "$LOG_DIR/export_solid_only_stdout.log"
