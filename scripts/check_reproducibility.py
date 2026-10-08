from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
INTERIM = ROOT / "data" / "interim"

required = {
    "00 — подготовленная панель":
        "consumption_total_wide_2016x24.parquet",
    "01 — Prophet benchmark":
        "baseline_multihorizon_summary.csv",
    "02 — географические соответствия":
        "consumption_series_geography.parquet",
    "02 — сезонные кластеры":
        "seasonal_cluster_map_k5.parquet",
    "03 — история экспертов":
        "adaptive_expert_history.parquet",
    "04 — сравнение детекторов":
        "shock_detector_four_method_test_comparison.csv",
    "05 — реальные эпизоды":
        "shock_real_cases_summary.csv",
    "05 — News Alignment":
        "shock_news_alignment_quantitative_top10.csv",
    "06 — итоговая сводка":
        "final_results_summary.csv",
}

missing = []

print("SHOCK RADAR — REPRODUCIBILITY CHECK\n")

for stage, filename in required.items():
    path = INTERIM / filename
    exists = path.is_file() and path.stat().st_size > 0

    print(f"{'OK' if exists else 'MISSING':8} {stage}: {filename}")

    if not exists:
        missing.append(filename)

print(f"\nChecked: {len(required)}")
print(f"Missing: {len(missing)}")

if missing:
    print(
        "\nSome notebooks require prepared input artifacts. "
        "See data/README.md."
    )
    sys.exit(1)

print("\nPrepared-artifact availability: PASSED")
