from __future__ import annotations

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score


def _logit_feature(probabilities: np.ndarray) -> np.ndarray:
    p = np.clip(np.asarray(probabilities, dtype=float), 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p)).reshape(-1, 1)


def fit_platt_calibrator(raw_probabilities: np.ndarray, y_true: np.ndarray):
    y = np.asarray(y_true, dtype=int)

    if np.unique(y).size < 2:
        return None

    calibrator = LogisticRegression(solver="lbfgs")
    calibrator.fit(_logit_feature(raw_probabilities), y)
    return calibrator


def apply_calibration(raw_probabilities: np.ndarray, calibrator) -> np.ndarray:
    raw = np.asarray(raw_probabilities, dtype=float)

    if calibrator is None:
        return np.clip(raw, 0.0, 1.0)

    return calibrator.predict_proba(_logit_feature(raw))[:, 1]


def best_f1_threshold(
    y_true: np.ndarray,
    probabilities: np.ndarray,
    default: float = 0.50,
) -> float:
    y = np.asarray(y_true, dtype=int)
    p = np.asarray(probabilities, dtype=float)

    if np.unique(y).size < 2:
        return float(default)

    best_threshold = float(default)
    best_score = -1.0

    for threshold in np.linspace(0.20, 0.80, 61):
        score = f1_score(y, (p >= threshold).astype(int), zero_division=0)
        if score > best_score:
            best_score = score
            best_threshold = float(threshold)

    return round(best_threshold, 3)


def probability_label(probability: float) -> str:
    p = float(probability)

    if p < 0.20:
        return "Very Low"
    if p < 0.40:
        return "Low"
    if p < 0.60:
        return "Moderate"
    if p < 0.80:
        return "High"
    return "Very High"
