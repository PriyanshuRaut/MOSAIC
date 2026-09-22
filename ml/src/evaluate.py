from __future__ import annotations

import json

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    f1_score,
    log_loss,
    precision_score,
    recall_score,
    roc_auc_score,
)

from .probability import apply_calibration
from .train import filter_target_rows
from .utils import MODELS_DIR, PROCESSED_DIR, load_config


def calculate_metrics(y_true, probabilities, threshold):
    predictions = (probabilities >= threshold).astype(int)
    metrics = {
        "samples": int(len(y_true)),
        "event_rate": float(np.mean(y_true)),
        "brier_score": float(brier_score_loss(y_true, probabilities)),
        "log_loss": float(log_loss(y_true, probabilities, labels=[0, 1])),
        "precision": float(precision_score(y_true, predictions, zero_division=0)),
        "recall": float(recall_score(y_true, predictions, zero_division=0)),
        "f1": float(f1_score(y_true, predictions, zero_division=0)),
    }
    if np.unique(y_true).size > 1:
        metrics["roc_auc"] = float(roc_auc_score(y_true, probabilities))
        metrics["average_precision"] = float(average_precision_score(y_true, probabilities))
    else:
        metrics["roc_auc"] = None
        metrics["average_precision"] = None
    return metrics


def baseline_probabilities(train: pd.DataFrame, test: pd.DataFrame, target: str) -> np.ndarray:
    by_lead = train.groupby("lead_week")[target].mean().to_dict()
    overall = float(train[target].mean())
    return test["lead_week"].map(lambda w: by_lead.get(w, overall)).astype(float).to_numpy()


def main() -> None:
    config = load_config()
    train_all = pd.read_csv(PROCESSED_DIR / "train.csv")
    test_all = pd.read_csv(PROCESSED_DIR / "test.csv")
    report = {}

    for target in config["targets"]:
        artifact = joblib.load(MODELS_DIR / f"{target}_model.pkl")
        features = artifact["numeric_features"] + artifact["categorical_features"]
        train = filter_target_rows(train_all, target, config)
        test = filter_target_rows(test_all, target, config)

        y = test[target].astype(int).to_numpy()
        raw = artifact["model"].predict_proba(test[features])[:, 1]
        prob = apply_calibration(raw, artifact["calibrator"])
        threshold = float(artifact["threshold"])
        overall = calculate_metrics(y, prob, threshold)

        baseline = baseline_probabilities(train, test, target)
        baseline_brier = float(brier_score_loss(y, baseline))
        overall["climatology_brier_score"] = baseline_brier
        overall["brier_skill_score_vs_climatology"] = (
            float(1.0 - overall["brier_score"] / baseline_brier) if baseline_brier > 0 else None
        )

        per_lead = {}
        for lead in (1, 2, 3, 4):
            mask = test["lead_week"].to_numpy() == lead
            if not mask.any():
                continue
            per_lead[str(lead)] = calculate_metrics(y[mask], prob[mask], threshold)

        report[target] = {
            "threshold": threshold,
            "overall": overall,
            "per_lead_week": per_lead,
        }

        print(f"\n{target.upper()}")
        for key, value in overall.items():
            if isinstance(value, float):
                print(f"{key:32s}: {value:.4f}")
            else:
                print(f"{key:32s}: {value}")
        print("Lead-week AUC / Brier:")
        for lead, metrics in per_lead.items():
            print(
                f"  W{lead}: AUC={metrics['roc_auc']} | "
                f"Brier={metrics['brier_score']:.4f} | F1={metrics['f1']:.4f}"
            )

    output = MODELS_DIR / "evaluation.json"
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nSaved evaluation report to {output}")


if __name__ == "__main__":
    main()
