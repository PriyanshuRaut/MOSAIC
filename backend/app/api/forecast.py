from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.app.schemas.forecast import ForecastRequest, ForecastResponse
from backend.app.services.model_service import model_service

router = APIRouter(prefix="/api", tags=["Forecast"])


@router.post("/predict", response_model=ForecastResponse)
def predict(request: ForecastRequest) -> dict:
    try:
        payload = request.model_dump(mode="json")
        return model_service.predict(payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}") from exc
