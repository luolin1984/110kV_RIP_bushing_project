#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
COMSOL_BIN="/Applications/COMSOL60/Multiphysics/bin/comsol"
PYTHON_BIN="/Users/luolin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"
LOG_DIR="${PROJECT_DIR}/results/raw_comsol_exports/MATERIAL_AND_MESH_SENSITIVITY_RUN011"

mkdir -p "${LOG_DIR}"
cd "${PROJECT_DIR}"

export BRFGL1_PROJECT_ROOT="${PROJECT_DIR}"

"${COMSOL_BIN}" compile "${PROJECT_DIR}/comsol/run_material_and_mesh_sensitivity_run011.java" \
  2>&1 | tee "${LOG_DIR}/compile_run011.log"

"${COMSOL_BIN}" batch -autosave off \
  -inputfile "${PROJECT_DIR}/comsol/run_material_and_mesh_sensitivity_run011.class" \
  -batchlog "${LOG_DIR}/run011_batch.log" \
  -batchlogout \
  2>&1 | tee "${LOG_DIR}/run011_stdout.log"

"${PYTHON_BIN}" "${PROJECT_DIR}/scripts/plot_material_and_mesh_sensitivity_run011.py" \
  2>&1 | tee "${LOG_DIR}/postprocess_run011.log"
