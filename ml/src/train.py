from __future__ import annotations

import json
from datetime import datetime, timezone

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBClassifier

from .probability import apply_calibration, best_f1_threshold, fit_platt_calibrator
from .utils import MODELS_DIR, PROCESSED_DIR, ensure_directories, load_config, set_seed


def build_pipeline(numeric_features, categorical_features, model_params, random_seed, scale_pos_weight):
    numeric = Pipeline([("imputer", SimpleImputer(strategy="median"))])
    categorical = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    preprocessor = ColumnTransformer(
        [
            ("numeric", numeric, numeric_features),
            ("categorical", categorical, categorical_features),
        ],
        remainder="drop",
    )
    model = XGBClassifier(
        objective="binary:logistic",
        eval_metric="logloss",
        random_state=random_seed,
        n_jobs=-1,
        scale_pos_weight=scale_pos_weight,
        **model_params,
    )
    return Pipeline([("preprocessor", preprocessor), ("model", model)])


def class_weight(y: pd.Series) -> float:
    positives = int((y == 1).sum())
    negatives = int((y == 0).sum())
    if positives == 0:
        return 1.0
    return max(0.25, min(12.0, negatives / positives))


def validation_summary(y_true, probabilities):
    result = {"brier_score": float(brier_score_loss(y_true, probabilities))}
    result["roc_auc"] = float(roc_auc_score(y_true, probabilities)) if np.unique(y_true).size > 1 else None
    return result


def filter_target_rows(df: pd.DataFrame, target: str, config: dict) -> pd.DataFrame:
    months = config.get("target_issue_months", {}).get(target)
    if months:
        return df[df["month"].isin(months)].copy()
    return df.copy()


def main() -> None:
    config = load_config()
    ensure_directories()
    seed = int(config["random_seed"])
    set_seed(seed)

    train_all = pd.read_csv(PROCESSED_DIR / "train.csv")
    validation_all = pd.read_csv(PROCESSED_DIR / "validation.csv")

    numeric_features = config["numeric_features"]
    categorical_features = config["categorical_features"]
    all_features = numeric_features + categorical_features

    missing = sorted(set(all_features) - set(train_all.columns))
    if missing:
        raise ValueError(f"Processed training data is missing: {missing}")

    manifest = {
        "trained_at_utc": datetime.now(timezone.utc).isoformat(),
        "data_mode": "real_historical_public_sources",
        "targets": {},
    }

    for target in config["targets"]:
        print(f"\nTraining {target} model...")
        train = filter_target_rows(train_all, target, config)
        validation = filter_target_rows(validation_all, target, config)

        y_train = train[target].astype(int)
        y_validation = validation[target].astype(int)
        print(
            f"Rows: train={len(train):,}, validation={len(validation):,} | "
            f"positive rate={y_train.mean():.4f}"
        )

        if y_train.nunique() < 2:
            raise ValueError(f"Target {target} has only one class in training data.")

        pipeline = build_pipeline(
            numeric_features,
            categorical_features,
            config["xgboost"],
            seed,
            class_weight(y_train),
        )
        pipeline.fit(train[all_features], y_train)

        raw_prob = pipeline.predict_proba(validation[all_features])[:, 1]
        calibrator = fit_platt_calibrator(raw_prob, y_validation.to_numpy())
        calibrated = apply_calibration(raw_prob, calibrator)
        threshold = best_f1_threshold(
            y_validation.to_numpy(), calibrated, float(config["probability"]["default_threshold"])
        )
        metrics = validation_summary(y_validation.to_numpy(), calibrated)

        artifact = {
            "target": target,
            "model": pipeline,
            "calibrator": calibrator,
            "threshold": threshold,
            "numeric_features": numeric_features,
            "categorical_features": categorical_features,
            "trained_at_utc": manifest["trained_at_utc"],
            "training_years": config["split"],
            "data_mode": "real_historical_public_sources",
            "validation_metrics": metrics,
        }
        output = MODELS_DIR / f"{target}_model.pkl"
        joblib.dump(artifact, output)
        manifest["targets"][target] = {
            "model_file": output.name,
            "threshold": threshold,
            "training_rows": int(len(train)),
            "validation_rows": int(len(validation)),
            "training_positive_rate": float(y_train.mean()),
            **metrics,
        }
        print(
            f"Saved {output.name} | threshold={threshold:.3f} | "
            f"Brier={metrics['brier_score']:.4f} | AUC={metrics['roc_auc']}"
        )

    with (MODELS_DIR / "manifest.json").open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print("\nAll four historical MOSAIC models trained successfully.")


if __name__ == "__main__":
    main()
