from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from backend.app.core.config import MODELS_DIR, TARGETS
from ml.src.features import engineer_features
from ml.src.probability import apply_calibration, probability_label


class ModelService:
    def __init__(self) -> None:
        self.artifacts: dict[str, dict[str, Any]] = {}
        self.manifest: dict[str, Any] = {}
        self.evaluation: dict[str, Any] = {}

    @property
    def loaded(self) -> bool:
        return len(self.artifacts) == len(TARGETS)

    def load(self) -> None:
        missing = [
            str(MODELS_DIR / f"{target}_model.pkl")
            for target in TARGETS
            if not (MODELS_DIR / f"{target}_model.pkl").exists()
        ]
        if missing:
            raise FileNotFoundError(
                "MOSAIC model files are missing:\n" + "\n".join(missing)
            )

        self.artifacts = {
            target: joblib.load(MODELS_DIR / f"{target}_model.pkl")
            for target in TARGETS
        }

        manifest_path = MODELS_DIR / "manifest.json"
        evaluation_path = MODELS_DIR / "evaluation.json"

        self.manifest = self._read_json(manifest_path)
        self.evaluation = self._read_json(evaluation_path)

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    @staticmethod
    def _ensure_model_columns(
        dataframe: pd.DataFrame,
        artifact: dict[str, Any],
    ) -> pd.DataFrame:
        columns = artifact["numeric_features"] + artifact["categorical_features"]
        result = dataframe.copy()

        for column in columns:
            if column not in result.columns:
                result[column] = np.nan

        return result[columns]

    @staticmethod
    def _expand_payload(payload: dict[str, Any]) -> list[dict[str, Any]]:
        base = {key: value for key, value in payload.items() if key != "weeks"}
        weeks = payload.get("weeks") or [{"lead_week": week} for week in (1, 2, 3, 4)]

        rows: list[dict[str, Any]] = []
        for week in weeks:
            row = base.copy()
            row.update(week)
            rows.append(row)

        return rows

    def predict(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not self.loaded:
            self.load()

        rows = self._expand_payload(payload)
        engineered = engineer_features(pd.DataFrame(rows))

        week_results: list[dict[str, Any]] = []

        for row_index in range(len(engineered)):
            result: dict[str, Any] = {
                "lead_week": int(engineered.iloc[row_index]["lead_week"]),
                "probabilities": {},
            }

            for target, artifact in self.artifacts.items():
                row = engineered.iloc[[row_index]]
                model_input = self._ensure_model_columns(row, artifact)

                raw_probability = artifact["model"].predict_proba(model_input)[:, 1]
                probability = float(
                    apply_calibration(raw_probability, artifact["calibrator"])[0]
                )
                probability = min(1.0, max(0.0, probability))

                result["probabilities"][target] = {
                    "probability": round(probability, 4),
                    "percent": round(probability * 100.0, 1),
                    "level": probability_label(probability),
                    "event": bool(probability >= float(artifact["threshold"])),
                    "threshold": float(artifact["threshold"]),
                }

            week_results.append(result)

        trained_at = None
        if self.manifest:
            trained_at = self.manifest.get("trained_at_utc")

        return {
            "location": {
                "state": payload["state"],
                "district": payload["district"],
                "block": payload["block"],
                "panchayat": payload["panchayat"],
            },
            "forecast_date": str(payload["date"]),
            "weeks": week_results,
            "model": {
                "version": "historical-baseline-v1",
                "trained_at_utc": trained_at,
                "targets": list(TARGETS),
                "data_mode": "real_historical_public_sources",
            },
            "disclaimer": (
                "Research/prototype forecast. The current baseline was trained on "
                "historical public climate/weather data from a limited set of locations "
                "and is not an official IMD/NCMRWF operational warning."
            ),
        }

    def info(self) -> dict[str, Any]:
        if not self.loaded:
            self.load()

        return {
            "loaded": True,
            "targets": list(TARGETS),
            "model_directory": str(MODELS_DIR),
            "manifest": self.manifest,
            "evaluation": self.evaluation,
            "limitations": [
                "Historical baseline currently covers a limited set of representative Indian locations.",
                "NASA POWER inputs are not Panchayat-resolution observations.",
                "Historical NCMRWF/IMD forecast hindcasts are not yet included.",
                "Forecast probabilities are research/prototype outputs, not official warnings.",
            ],
        }


model_service = ModelService()
