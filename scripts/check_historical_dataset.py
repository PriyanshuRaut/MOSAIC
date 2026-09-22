from __future__ import annotations

from pathlib import Path
import pandas as pd

PATH = Path("ml/data/raw/mosaic_training.csv")


def main():
    df = pd.read_csv(PATH)
    print(f"Rows: {len(df):,}")
    print(f"Dates: {df['date'].min()} -> {df['date'].max()}")
    print(f"Locations: {df[['state','district','block','panchayat']].drop_duplicates().shape[0]}")

    print("\nClimate feature coverage:")
    climate_columns = ["enso", "iod", "mjo_phase", "mjo_amplitude", "rmm1", "rmm2"]
    for column in climate_columns:
        present = (1.0 - df[column].isna().mean()) * 100.0
        print(f"{column:14s}: {present:6.2f}% present")

    print("\nMissing % (top 15):")
    print((df.isna().mean().sort_values(ascending=False).head(15) * 100).round(2))

    critical = ["enso", "iod", "mjo_phase", "mjo_amplitude"]
    broken = [column for column in critical if df[column].isna().all()]
    if broken:
        raise SystemExit(
            "\nERROR: Critical climate features are completely missing: "
            + ", ".join(broken)
            + "\nDo not train until this is fixed."
        )

    print("\nTarget balance:")
    for target in ["onset", "break", "revival", "heavy_rain"]:
        print(f"{target:12s}: {df[target].mean():.4%}")

    print("\nDataset integrity check: PASS")


if __name__ == "__main__":
    main()
