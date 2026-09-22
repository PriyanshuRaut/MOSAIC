from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.app.services.model_service import model_service

router = APIRouter(prefix="/api", tags=["Model"])


@router.get("/model-info")
def model_info() -> dict:
    try:
        return model_service.info()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Could not read model info: {exc}") from exc
