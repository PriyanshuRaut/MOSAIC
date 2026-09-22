from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pandas as pd

from ml.src.data_sources import (
    download_mjo,
    download_monthly_indices,
    download_power_daily,
    make_session,
)
from ml.src.historical_builder import Location, build_location_training_rows, merge_climate_indices

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "ml" / "data" / "raw"
HIST_DIR = RAW_DIR / "historical"
DEFAULT_LOCATIONS = ROOT / "shared" / "sample-data" / "historical_locations.csv"
OUTPUT = RAW_DIR / "mosaic_training.csv"


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def read_locations(path: Path) -> list[Location]:
    frame = pd.read_csv(path)
    required = {"state", "district", "block", "panchayat", "latitude", "longitude"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Locations CSV missing columns: {sorted(missing)}")
    return [
        Location(
            state=str(row.state), district=str(row.district), block=str(row.block),
            panchayat=str(row.panchayat), latitude=float(row.latitude), longitude=float(row.longitude)
        )
        for row in frame.itertuples(index=False)
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build MOSAIC from real historical public climate data.")
    parser.add_argument("--locations", type=Path, default=DEFAULT_LOCATIONS)
    parser.add_argument("--start", default="2001-01-01")
    parser.add_argument("--end", default="2025-12-31")
    args = parser.parse_args()

    HIST_DIR.mkdir(parents=True, exist_ok=True)
    session = make_session()
    print("Downloading/loading ENSO and IOD monthly indices...")
    enso, iod = download_monthly_indices(HIST_DIR / "indices", session)
    print(f"ENSO rows: {len(enso):,} | IOD rows: {len(iod):,}")
    print(f"ENSO range: {enso['date'].min()} -> {enso['date'].max()}")
    print(f"IOD range : {iod['date'].min()} -> {iod['date'].max()}")

    print("Downloading/loading BOM daily MJO RMM index...")
    mjo = download_mjo(HIST_DIR / "indices", session)
    print(f"MJO rows: {len(mjo):,}")
    print(f"MJO range : {mjo['date'].min()} -> {mjo['date'].max()}")

    locations = read_locations(args.locations)
    all_rows = []
    source_summary = []

    for i, location in enumerate(locations, start=1):
        label = f"{location.district}, {location.state}"
        print(f"\n[{i}/{len(locations)}] NASA POWER: {label}")
        slug = slugify(f"{location.state}-{location.district}-{location.latitude}-{location.longitude}")
        cache = HIST_DIR / "power" / f"{slug}_{args.start}_{args.end}.json"
        weather = download_power_daily(
            location.latitude, location.longitude, args.start, args.end, cache, session
        )
        merged = merge_climate_indices(weather, enso, iod, mjo)
        rows = build_location_training_rows(merged, location)
        print(f"Built {len(rows):,} training rows")
        all_rows.append(rows)
        source_summary.append(
            {
                "state": location.state,
                "district": location.district,
                "latitude": location.latitude,
                "longitude": location.longitude,
                "daily_rows": len(weather),
                "training_rows": len(rows),
            }
        )

    dataset = pd.concat(all_rows, ignore_index=True)
    dataset = dataset.sort_values(["date", "state", "district", "lead_week"]).reset_index(drop=True)

    climate_columns = ["enso", "iod", "mjo_phase", "mjo_amplitude", "rmm1", "rmm2"]
    print("\nClimate-index coverage in assembled dataset:")
    for column in climate_columns:
        missing_pct = float(dataset[column].isna().mean() * 100.0)
        print(f"  {column:14s}: {100.0 - missing_pct:6.2f}% present | {missing_pct:6.2f}% missing")

    critical = ["enso", "iod", "mjo_phase", "mjo_amplitude"]
    broken = [column for column in critical if dataset[column].isna().all()]
    if broken:
        raise RuntimeError(
            "Critical climate features are completely missing: "
            + ", ".join(broken)
            + ". Do not train. Check the index parser/merge first."
        )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    dataset.to_csv(OUTPUT, index=False)

    metadata = {
        "dataset": str(OUTPUT.relative_to(ROOT)),
        "start": args.start,
        "end": args.end,
        "rows": int(len(dataset)),
        "locations": source_summary,
        "sources": {
            "daily_weather": "NASA POWER daily point API: PRECTOTCORR, T2M, RH2M, WS2M, GWETROOT",
            "enso": "NOAA PSL/CPC Nino 3.4 monthly anomaly",
            "iod": "NOAA PSL Dipole Mode Index (DMI)",
            "mjo": "Australian Bureau of Meteorology RMM daily index",
        },
        "labels": {
            "onset": "Agricultural onset proxy: first 5-day wet establishment with follow-through; not official IMD onset.",
            "break": "7-day target window <=10 mm and >=5 dry days (<1 mm).",
            "revival": "Prior 7-day dry spell <=10 mm followed by >=25 mm and >=3 wet days in target week.",
            "heavy_rain": "At least one target-window day >=64.5 mm.",
        },
        "target_positive_rates": {
            target: float(dataset[target].mean())
            for target in ["onset", "break", "revival", "heavy_rain"]
        },
    }
    (RAW_DIR / "historical_dataset_metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )

    print(f"\nSaved REAL historical training dataset: {OUTPUT}")
    print(f"Rows: {len(dataset):,}")
    print("Positive rates:")
    for target, rate in metadata["target_positive_rates"].items():
        print(f"  {target:12s}: {rate:.4%}")
    print("\nNext: python -m scripts.train_all_models")


if __name__ == "__main__":
    main()
