from __future__ import annotations

import numpy as np
import pandas as pd

BASE_COLUMNS = [
    "date",
    "state",
    "district",
    "block",
    "panchayat",
    "latitude",
    "longitude",
    "lead_week",
    "rainfall_1d",
    "rainfall_3d",
    "rainfall_7d",
    "rainfall_14d",
    "rainfall_30d",
    "rainfall_anomaly_pct",
    "rainy_days_7d",
    "dry_days_7d",
    "soil_moisture",
    "soil_moisture_7d_mean",
    "humidity",
    "humidity_7d_mean",
    "temperature_c",
    "temperature_7d_mean",
    "wind_speed_ms",
    "wind_7d_mean",
    "enso",
    "iod",
    "mjo_phase",
    "mjo_amplitude",
    "rmm1",
    "rmm2",
]


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()

    if "date" not in data.columns:
        raise ValueError("Missing required column: date")

    data["date"] = pd.to_datetime(data["date"], errors="coerce")
    if data["date"].isna().any():
        raise ValueError("One or more rows contain an invalid date.")

    data["month"] = data["date"].dt.month.astype(int)
    data["week_of_year"] = data["date"].dt.isocalendar().week.astype(int)
    data["day_of_year"] = data["date"].dt.dayofyear.astype(int)

    data["month_sin"] = np.sin(2 * np.pi * data["month"] / 12.0)
    data["month_cos"] = np.cos(2 * np.pi * data["month"] / 12.0)
    data["doy_sin"] = np.sin(2 * np.pi * data["day_of_year"] / 365.25)
    data["doy_cos"] = np.cos(2 * np.pi * data["day_of_year"] / 365.25)

    phase = pd.to_numeric(data.get("mjo_phase"), errors="coerce")
    amp = pd.to_numeric(data.get("mjo_amplitude"), errors="coerce")
    data["mjo_phase_sin"] = np.sin(2 * np.pi * phase / 8.0)
    data["mjo_phase_cos"] = np.cos(2 * np.pi * phase / 8.0)
    data["mjo_active"] = (amp >= 1.0).astype(float)

    rain_3 = pd.to_numeric(data.get("rainfall_3d"), errors="coerce")
    rain_7 = pd.to_numeric(data.get("rainfall_7d"), errors="coerce")
    rain_14 = pd.to_numeric(data.get("rainfall_14d"), errors="coerce")
    soil = pd.to_numeric(data.get("soil_moisture"), errors="coerce")

    data["rainfall_7d_mean"] = rain_7 / 7.0
    data["rainfall_14d_mean"] = rain_14 / 14.0
    data["rainfall_acceleration"] = (rain_3 / 3.0) - (rain_14 / 14.0)
    data["recent_rain_share"] = rain_7 / (rain_14.abs() + 1.0)
    data["soil_rain_interaction"] = soil * rain_7
    data["enso_iod_interaction"] = (
        pd.to_numeric(data.get("enso"), errors="coerce")
        * pd.to_numeric(data.get("iod"), errors="coerce")
    )

    return data
