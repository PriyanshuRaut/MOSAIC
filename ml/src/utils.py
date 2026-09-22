from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

import numpy as np
import yaml

ML_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ML_ROOT.parent
CONFIG_PATH = ML_ROOT / "config" / "model_config.yaml"
PROCESSED_DIR = ML_ROOT / "data" / "processed"
MODELS_DIR = ML_ROOT / "models"


def load_config(path: Path | None = None) -> dict[str, Any]:
    path = path or CONFIG_PATH
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def ensure_directories() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)


def save_json(data: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
