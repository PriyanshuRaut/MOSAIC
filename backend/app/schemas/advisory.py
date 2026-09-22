from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from .forecast import ForecastRequest, ForecastResponse


CropStage = Literal[
    "pre-sowing",
    "sowing",
    "germination",
    "vegetative",
    "flowering",
    "harvest",
]


class AdvisoryRequest(BaseModel):
    forecast: ForecastRequest
    crop: str = Field(min_length=1)
    crop_stage: CropStage
    irrigation_available: bool = False
    language: str = "English"


class WeeklyAdvisory(BaseModel):
    lead_week: int
    risk_summary: str
    actions: list[str]


class AdvisoryResponse(BaseModel):
    crop: str
    crop_stage: str
    irrigation_available: bool
    forecast: ForecastResponse
    overall_advisory: str
    weekly_advisories: list[WeeklyAdvisory]
    disclaimer: str
