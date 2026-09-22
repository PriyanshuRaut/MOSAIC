from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
BACKEND_DIR = PROJECT_ROOT / "backend"
MODELS_DIR = PROJECT_ROOT / "ml" / "models"
DATASET_PATH = PROJECT_ROOT / "ml" / "data" / "raw" / "mosaic_training.csv"

load_dotenv(BACKEND_DIR / ".env")

APP_NAME = "MOSAIC Monsoon Intelligence API"
APP_VERSION = "1.0.0"

HOST = os.getenv("MOSAIC_API_HOST", "127.0.0.1")
PORT = int(os.getenv("MOSAIC_API_PORT", "8000"))

CORS_ORIGINS = [
    value.strip()
    for value in os.getenv(
        "MOSAIC_CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    ).split(",")
    if value.strip()
]

TARGETS = ("onset", "break", "revival", "heavy_rain")
