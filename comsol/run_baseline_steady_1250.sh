#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
COMSOL_BIN="/Applications/COMSOL60/Multiphysics/bin/comsol"
PHYSICS_JAVA="$PROJECT_DIR/comsol/build_physics_brfgl1.java"
PHYSICS_CLASS="$PROJECT_DIR/comsol/build_physics_brfgl1.class"
RUN_JAVA="$PROJECT_DIR/comsol/run_baseline_steady_1250.java"
RUN_CLASS="$PROJECT_DIR/comsol/run_baseline_steady_1250.class"
PHYSICS_MPH="$PROJECT_DIR/comsol/BRFGL1-126-1250-4_physics_baseline.mph"
BASELINE_MPH="$PROJECT_DIR/comsol/BRFGL1-126-1250-4_baseline_STEADY_1250_LOAD_1p0_RUN002.mph"
LOG_DIR="$PROJECT_DIR/results/raw_comsol_exports/STEADY_1250_LOAD_1p0_RUN002"

mkdir -p "$LOG_DIR"
export BRFGL1_PROJECT_ROOT="$PROJECT_DIR"

"$COMSOL_BIN" compile "$PHYSICS_JAVA" 2>&1 | tee "$LOG_DIR/compile_physics.log"
"$COMSOL_BIN" batch \
  -autosave off \
  -inputfile "$PHYSICS_CLASS" \
  -outputfile "$PHYSICS_MPH" \
  -batchlog "$LOG_DIR/build_physics_batch.log" \
  -batchlogout 2>&1 | tee "$LOG_DIR/build_physics_stdout.log"

"$COMSOL_BIN" compile "$RUN_JAVA" 2>&1 | tee "$LOG_DIR/compile_run.log"
"$COMSOL_BIN" batch \
  -autosave off \
  -inputfile "$RUN_CLASS" \
  -outputfile "$BASELINE_MPH" \
  -batchlog "$LOG_DIR/run_baseline_batch.log" \
  -batchlogout 2>&1 | tee "$LOG_DIR/run_baseline_stdout.log"
