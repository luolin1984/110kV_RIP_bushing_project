#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
COMSOL_BIN="/Applications/COMSOL60/Multiphysics/bin/comsol"
BUILD_JAVA="$PROJECT_DIR/comsol/build_geometry_brfgl1.java"
BUILD_CLASS="$PROJECT_DIR/comsol/build_geometry_brfgl1.class"
OUT_MPH="$PROJECT_DIR/comsol/BRFGL1-126-1250-4_geometry_axisym.mph"
LOG_DIR="$PROJECT_DIR/results/raw_comsol_exports/GEOMETRY_BRFGL1"

mkdir -p "$LOG_DIR"

cd "$PROJECT_DIR"
export BRFGL1_PROJECT_ROOT="$PROJECT_DIR"
"$COMSOL_BIN" compile "$BUILD_JAVA" 2>&1 | tee "$LOG_DIR/compile.log"
"$COMSOL_BIN" batch \
  -autosave off \
  -inputfile "$BUILD_CLASS" \
  -outputfile "$OUT_MPH" \
  -batchlog "$LOG_DIR/comsol_batch.log" \
  -batchlogout 2>&1 | tee "$LOG_DIR/run_stdout.log"
