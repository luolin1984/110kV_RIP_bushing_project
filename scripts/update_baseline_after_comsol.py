"""Update CSV templates after the first COMSOL baseline run.

This helper is intentionally conservative: it records that the baseline run was
attempted and leaves calibrated targets untouched unless a metrics CSV exported
from COMSOL is present.
"""

from __future__ import annotations

import csv
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
PROCESSED = PROJECT / "data" / "processed"
EXPORT_DIR = PROJECT / "results" / "raw_comsol_exports" / "STEADY_1250_LOAD_1p0"


def main() -> None:
    metrics_export = EXPORT_DIR / "metrics_export.csv"
    if not metrics_export.exists():
        print(f"No COMSOL metrics export found at {metrics_export}; templates left for calibration.")
        return

    rows = list(csv.DictReader((PROCESSED / "validation_targets.csv").open(newline="")))
    metrics = next(csv.DictReader(metrics_export.open(newline="")))
    mapping = {
        "Tmax_conductor_baseline": "Tmax_conductor",
        "Tmax_RIP_baseline": "Tmax_RIP",
        "Emax_RIP_baseline": "Emax_RIP",
        "Qdielectric_total_baseline": "Qdielectric_total",
    }
    for row in rows:
        key = mapping.get(row["quantity"])
        if key and metrics.get(key):
            row["expected_value"] = metrics[key]
            row["source"] = "First COMSOL baseline run STEADY_1250_LOAD_1p0"
            row["source_id"] = "COMSOL_BASELINE_RUN_001"
            row["notes"] = "Backfilled from first baseline model run."

    with (PROCESSED / "validation_targets.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
