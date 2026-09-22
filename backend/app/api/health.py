from __future__ import annotations

from fastapi import APIRouter

from backend.app.core.config import APP_VERSION, MODELS_DIR
from backend.app.services.model_service import model_service

router = APIRouter(prefix="/api", tags=["System"])


@router.get("/health")
def health() -> dict:
    return {
        "status": "ok" if model_service.loaded else "starting",
        "api_version": APP_VERSION,
        "models_loaded": model_service.loaded,
        "model_directory": str(MODELS_DIR),
    }
