from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.app.schemas.advisory import AdvisoryRequest, AdvisoryResponse
from backend.app.services.advisory_service import build_advisory
from backend.app.services.model_service import model_service

router = APIRouter(prefix="/api", tags=["Advisory"])


@router.post("/advisory", response_model=AdvisoryResponse)
def advisory(request: AdvisoryRequest) -> dict:
    try:
        forecast_payload = request.forecast.model_dump(mode="json")
        forecast = model_service.predict(forecast_payload)

        advisory_result = build_advisory(
            forecast=forecast,
            crop=request.crop,
            crop_stage=request.crop_stage,
            irrigation_available=request.irrigation_available,
        )

        return {
            "crop": request.crop,
            "crop_stage": request.crop_stage,
            "irrigation_available": request.irrigation_available,
            "forecast": forecast,
            "overall_advisory": advisory_result["overall_advisory"],
            "weekly_advisories": advisory_result["weekly_advisories"],
            "disclaimer": (
                "Prototype agronomic decision support only. Advisory rules have not yet "
                "been validated by ICAR/KVK or state agricultural authorities."
            ),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Advisory generation failed: {exc}") from exc
