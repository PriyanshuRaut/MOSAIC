from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .features import BASE_COLUMNS, engineer_features
from .utils import PROCESSED_DIR, ensure_directories, load_config


def validate_columns(df: pd.DataFrame, targets: list[str]) -> None:
    required = set(BASE_COLUMNS + targets)
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError("Dataset is missing required columns:\n- " + "\n- ".join(missing))


def year_split(
    df: pd.DataFrame,
    train_end_year: int,
    validation_end_year: int,
    test_end_year: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    years = pd.to_datetime(df["date"]).dt.year
    train = df[years <= train_end_year].copy()
    validation = df[(years > train_end_year) & (years <= validation_end_year)].copy()
    test = df[(years > validation_end_year) & (years <= test_end_year)].copy()

    if train.empty or validation.empty or test.empty:
        raise ValueError(
            "Year split produced an empty partition. Check the downloaded date range "
            "or edit ml/config/model_config.yaml."
        )
    return train, validation, test


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("ml/data/raw/mosaic_training.csv"),
        help="Historical MOSAIC training CSV.",
    )
    args = parser.parse_args()

    config = load_config()
    ensure_directories()

    df = pd.read_csv(args.input)
    validate_columns(df, config["targets"])

    all_missing = [column for column in BASE_COLUMNS if df[column].isna().all()]
    if all_missing:
        raise ValueError(
            "Required model features are completely missing: "
            + ", ".join(all_missing)
            + ". Rebuild/fix the historical dataset before training."
        )

    df = engineer_features(df)
    df = df.sort_values(["date", "state", "district", "block", "panchayat", "lead_week"]).reset_index(drop=True)

    split = config["split"]
    train, validation, test = year_split(
        df,
        train_end_year=int(split["train_end_year"]),
        validation_end_year=int(split["validation_end_year"]),
        test_end_year=int(split["test_end_year"]),
    )

    train.to_csv(PROCESSED_DIR / "train.csv", index=False)
    validation.to_csv(PROCESSED_DIR / "validation.csv", index=False)
    test.to_csv(PROCESSED_DIR / "test.csv", index=False)

    print(f"Saved train:      {len(train):,} rows ({train['date'].min()} to {train['date'].max()})")
    print(f"Saved validation: {len(validation):,} rows ({validation['date'].min()} to {validation['date'].max()})")
    print(f"Saved test:       {len(test):,} rows ({test['date'].min()} to {test['date'].max()})")


if __name__ == "__main__":
    main()
