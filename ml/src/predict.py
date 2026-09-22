from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from .features import engineer_features
from .probability import apply_calibration, probability_label
from .utils import MODELS_DIR, load_config


def load_artifacts() -> dict[str, dict[str, Any]]:
    config = load_config()
    return {
        target: joblib.load(MODELS_DIR / f"{target}_model.pkl")
        for target in config["targets"]
    }


def _ensure_model_columns(df: pd.DataFrame, artifact: dict[str, Any]) -> pd.DataFrame:
    features = artifact["numeric_features"] + artifact["categorical_features"]
    data = df.copy()

    for column in features:
        if column not in data.columns:
            data[column] = np.nan

    return data[features]


def predict_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not rows:
        return []

    engineered = engineer_features(pd.DataFrame(rows))
    artifacts = load_artifacts()
    outputs: list[dict[str, Any]] = []

    for row_index in range(len(engineered)):
        result = {
            "lead_week": int(engineered.iloc[row_index]["lead_week"]),
            "probabilities": {},
        }

        for target, artifact in artifacts.items():
            row = engineered.iloc[[row_index]]
            model_input = _ensure_model_columns(row, artifact)

            raw_probability = artifact["model"].predict_proba(model_input)[:, 1]
            probability = float(
                apply_calibration(raw_probability, artifact["calibrator"])[0]
            )

            result["probabilities"][target] = {
                "probability": round(probability, 4),
                "percent": round(probability * 100.0, 1),
                "level": probability_label(probability),
                "event": bool(probability >= float(artifact["threshold"])),
                "threshold": float(artifact["threshold"]),
            }

        outputs.append(result)

    return outputs


def expand_payload(payload: dict[str, Any]) -> list[dict[str, Any]]:
    if "weeks" not in payload:
        return [payload]

    base = {key: value for key, value in payload.items() if key != "weeks"}
    rows = []

    for week in payload["weeks"]:
        row = base.copy()
        row.update(week)
        rows.append(row)

    return rows


def predict_forecast(payload: dict[str, Any]) -> dict[str, Any]:
    rows = expand_payload(payload)
    predictions = predict_rows(rows)

    return {
        "location": {
            "state": payload.get("state"),
            "district": payload.get("district"),
            "block": payload.get("block"),
            "panchayat": payload.get("panchayat"),
        },
        "forecast_date": payload.get("date"),
        "weeks": predictions,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    args = parser.parse_args()

    with args.input.open("r", encoding="utf-8") as f:
        payload = json.load(f)

    print(json.dumps(predict_forecast(payload), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
