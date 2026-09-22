from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class LeadWeek(BaseModel):
    lead_week: int = Field(ge=1, le=4)


class ForecastRequest(BaseModel):
    state: str = Field(min_length=1)
    district: str = Field(min_length=1)
    block: str = Field(min_length=1)
    panchayat: str = Field(min_length=1)

    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    date: date

    rainfall_1d: float
    rainfall_3d: float
    rainfall_7d: float
    rainfall_14d: float
    rainfall_30d: float
    rainfall_anomaly_pct: float

    rainy_days_7d: float = Field(ge=0, le=7)
    dry_days_7d: float = Field(ge=0, le=7)

    soil_moisture: float
    soil_moisture_7d_mean: float

    humidity: float
    humidity_7d_mean: float

    temperature_c: float
    temperature_7d_mean: float

    wind_speed_ms: float
    wind_7d_mean: float

    enso: float
    iod: float

    mjo_phase: int = Field(ge=1, le=8)
    mjo_amplitude: float = Field(ge=0)
    rmm1: float
    rmm2: float

    weeks: list[LeadWeek] = Field(
        default_factory=lambda: [
            LeadWeek(lead_week=1),
            LeadWeek(lead_week=2),
            LeadWeek(lead_week=3),
            LeadWeek(lead_week=4),
        ]
    )

    @field_validator("weeks")
    @classmethod
    def validate_weeks(cls, value: list[LeadWeek]) -> list[LeadWeek]:
        if not value:
            raise ValueError("At least one forecast lead week is required.")

        lead_weeks = [item.lead_week for item in value]
        if len(lead_weeks) != len(set(lead_weeks)):
            raise ValueError("Duplicate lead weeks are not allowed.")

        return sorted(value, key=lambda item: item.lead_week)


class ProbabilityResult(BaseModel):
    probability: float
    percent: float
    level: Literal["Very Low", "Low", "Moderate", "High", "Very High"]
    event: bool
    threshold: float


class WeekForecast(BaseModel):
    lead_week: int
    probabilities: dict[str, ProbabilityResult]


class LocationResult(BaseModel):
    state: str
    district: str
    block: str
    panchayat: str


class ForecastResponse(BaseModel):
    location: LocationResult
    forecast_date: str
    weeks: list[WeekForecast]
    model: dict
    disclaimer: str
