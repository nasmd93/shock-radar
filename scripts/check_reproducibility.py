"""
Shock Radar — submission and data availability checks.

Usage:
    python scripts/check_reproducibility.py
    python scripts/check_reproducibility.py --mode submission
    python scripts/check_reproducibility.py --mode data
    python scripts/check_reproducibility.py --mode all
"""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INTERIM = ROOT / "data" / "interim"

NOTEBOOKS = [
    "00_data_final.ipynb",
    "01_forecasting_baselines_final.ipynb",
    "02_forecasting_static_final.ipynb",
    "03_forecasting_final.ipynb",
    "04_shock_detector_final.ipynb",
    "05_real_shocks_and_attribution_final.ipynb",
    "06_results_final.ipynb",
]

DOCUMENTS = [
    "README.md",
    "data/README.md",
    "requirements.txt",
    "configs/final_config.yaml",
    "reports/Shock_Radar_Methodology_RU.docx",
    "reports/Shock_Radar_Presentation_Green_RU.pdf",
]

DATA_ARTIFACTS = [
    "consumption_total_wide_2016x24.parquet",
    "baseline_multihorizon_summary.csv",
    "consumption_series_geography.parquet",
    "seasonal_cluster_map_k5.parquet",
    "adaptive_expert_history.parquet",
    "shock_detector_four_method_test_comparison.csv",
    "shock_real_cases_summary.csv",
    "shock_news_alignment_quantitative_top10.csv",
    "final_results_summary.csv",
]


def check_submission():
    print("\n=== SHOCK RADAR: SUBMISSION CHECK ===")

    errors = []
    total_outputs = 0

    for name in NOTEBOOKS:
        path = ROOT / "notebooks" / name

        if not path.is_file():
            print("MISSING", name)
            errors.append(name)
            continue

        try:
            notebook = json.loads(
                path.read_text(encoding="utf-8")
            )

            assert notebook.get("nbformat") == 4

            code_cells = [
                cell for cell in notebook["cells"]
                if cell["cell_type"] == "code"
            ]

            outputs = sum(
                len(cell.get("outputs", []))
                for cell in code_cells
            )

            total_outputs += outputs

            print(
                f"OK      {name} "
                f"({outputs} saved outputs)"
            )

        except (ValueError, KeyError, TypeError, AssertionError) as exc:
            print("INVALID", name, str(exc))
            errors.append(name)

    print("\n--- Documentation ---")

    for filename in DOCUMENTS:
        path = ROOT / filename
        ok = path.is_file() and path.stat().st_size > 0

        print(
            f"{'OK' if ok else 'MISSING':7} {filename}"
        )

        if not ok:
            errors.append(filename)

    print("\nSaved output objects:", total_outputs)

    if total_outputs == 0:
        errors.append("No saved notebook outputs")

    if errors:
        print("\nSUBMISSION CHECK: FAILED")
        return False

    print("\nSUBMISSION CHECK: PASSED")
    print(
        "Note: this verifies published materials, "
        "not their scientific correctness or full execution."
    )
    return True


def check_data():
    print("\n=== SHOCK RADAR: DATA AVAILABILITY ===")

    missing = []

    for filename in DATA_ARTIFACTS:
        path = INTERIM / filename

        ok = (
            path.is_file()
            and path.stat().st_size > 0
        )

        print(
            f"{'OK' if ok else 'MISSING':8} {filename}"
        )

        if not ok:
            missing.append(filename)

    print("\nChecked:", len(DATA_ARTIFACTS))
    print("Missing:", len(missing))

    if missing:
        print("\nDATA AVAILABILITY: INCOMPLETE")
        print(
            "Prepared artifacts are not all available. "
            "See data/README.md."
        )
        return False

    print("\nDATA AVAILABILITY: PASSED")
    print(
        "Note: this confirms nine key artifacts only. "
        "It does not verify all notebook dependencies "
        "or reproduce model calculations."
    )
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Shock Radar validation checks"
    )

    parser.add_argument(
        "--mode",
        choices=["submission", "data", "all"],
        default="submission",
    )

    args = parser.parse_args()

    results = []

    if args.mode in ("submission", "all"):
        results.append(check_submission())

    if args.mode in ("data", "all"):
        results.append(check_data())

    raise SystemExit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
