#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="/Users/luolin/Documents/New project/110kV_RIP_bushing_project"
COMSOL_BIN="/Applications/COMSOL60/Multiphysics/bin/comsol"
BUILD_JAVA="$PROJECT_DIR/comsol/build_model.java"
BUILD_CLASS="$PROJECT_DIR/comsol/build_model.class"
OUT_MPH="$PROJECT_DIR/comsol/BRFGL1-126-1250-4_base_model_2d_axisym_STEADY_1250_LOAD_1p0.mph"
LOG_DIR="$PROJECT_DIR/results/raw_comsol_exports/STEADY_1250_LOAD_1p0"

mkdir -p "$LOG_DIR"

"$COMSOL_BIN" compile "$BUILD_JAVA" 2>&1 | tee "$LOG_DIR/compile.log"
"$COMSOL_BIN" batch \
  -autosave off \
  -inputfile "$BUILD_CLASS" \
  -outputfile "$OUT_MPH" \
  -batchlog "$LOG_DIR/comsol_batch.log" \
  -batchlogout 2>&1 | tee "$LOG_DIR/run_stdout.log"
