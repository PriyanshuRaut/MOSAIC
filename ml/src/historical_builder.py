from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import numpy as np
import pandas as pd

HEAVY_RAIN_THRESHOLD_MM = 64.5
WET_DAY_MM = 2.5
DRY_DAY_MM = 1.0


@dataclass(frozen=True)
class Location:
    state: str
    district: str
    block: str
    panchayat: str
    latitude: float
    longitude: float


def _window(series: pd.Series, start_offset: int, days: int) -> pd.DataFrame:
    return pd.concat(
        [series.shift(-offset) for offset in range(start_offset, start_offset + days)],
        axis=1,
    )


def _find_agricultural_onset_dates(daily: pd.DataFrame) -> dict[int, pd.Timestamp]:
    """
    Agricultural onset proxy, NOT the official IMD monsoon onset definition.

    First date between 15 May and 31 July with:
      * >=25 mm over 5 days,
      * >=3 wet days (>2.5 mm) in those 5 days,
      * >=20 mm in the following 7 days.
    """
    frame = daily.set_index("date").sort_index()
    rainfall = frame["rainfall_mm"]
    onset_by_year: dict[int, pd.Timestamp] = {}

    for year in sorted(frame.index.year.unique()):
        start = pd.Timestamp(year, 5, 15)
        end = pd.Timestamp(year, 7, 31)
        candidates = frame.loc[(frame.index >= start) & (frame.index <= end)].index
        for candidate in candidates:
            first = rainfall.loc[candidate : candidate + pd.Timedelta(days=4)]
            follow = rainfall.loc[candidate + pd.Timedelta(days=5) : candidate + pd.Timedelta(days=11)]
            if len(first) < 5 or len(follow) < 7:
                continue
            if first.sum() >= 25.0 and (first >= WET_DAY_MM).sum() >= 3 and follow.sum() >= 20.0:
                onset_by_year[int(year)] = candidate
                break

    return onset_by_year


def add_observed_features(daily: pd.DataFrame) -> pd.DataFrame:
    data = daily.sort_values("date").copy()
    rain = data["rainfall_mm"].astype(float)

    data["rainfall_1d"] = rain
    data["rainfall_3d"] = rain.rolling(3, min_periods=3).sum()
    data["rainfall_7d"] = rain.rolling(7, min_periods=7).sum()
    data["rainfall_14d"] = rain.rolling(14, min_periods=14).sum()
    data["rainfall_30d"] = rain.rolling(30, min_periods=30).sum()
    data["rainy_days_7d"] = (rain >= WET_DAY_MM).rolling(7, min_periods=7).sum()
    data["dry_days_7d"] = (rain < DRY_DAY_MM).rolling(7, min_periods=7).sum()

    data["soil_moisture_7d_mean"] = data["soil_moisture"].rolling(7, min_periods=3).mean()
    data["humidity_7d_mean"] = data["humidity"].rolling(7, min_periods=3).mean()
    data["temperature_7d_mean"] = data["temperature_c"].rolling(7, min_periods=3).mean()
    data["wind_7d_mean"] = data["wind_speed_ms"].rolling(7, min_periods=3).mean()

    # Expanding same-month climatology using ONLY previous years.
    data["year"] = data["date"].dt.year
    data["month_num"] = data["date"].dt.month
    month_mean = (
        data.groupby(["year", "month_num"], as_index=False)["rainfall_mm"]
        .mean()
        .rename(columns={"rainfall_mm": "month_daily_mean"})
        .sort_values(["month_num", "year"])
    )
    month_mean["prior_clim_daily"] = (
        month_mean.groupby("month_num")["month_daily_mean"]
        .transform(lambda s: s.shift(1).expanding(min_periods=1).mean())
    )
    data = data.merge(
        month_mean[["year", "month_num", "prior_clim_daily"]],
        on=["year", "month_num"],
        how="left",
    )
    expected_14d = data["prior_clim_daily"] * 14.0
    data["rainfall_anomaly_pct"] = (
        100.0 * (data["rainfall_14d"] - expected_14d) / (expected_14d.abs() + 1.0)
    ).clip(-300, 700)

    return data


def merge_climate_indices(
    weather: pd.DataFrame,
    enso: pd.DataFrame,
    iod: pd.DataFrame,
    mjo: pd.DataFrame,
) -> pd.DataFrame:
    data = weather.copy()
    data["date"] = pd.to_datetime(data["date"])
    data["month_key"] = data["date"].dt.to_period("M").dt.to_timestamp()

    enso2 = enso.rename(columns={"date": "month_key"})
    iod2 = iod.rename(columns={"date": "month_key"})
    data = data.merge(enso2[["month_key", "enso"]], on="month_key", how="left")
    data = data.merge(iod2[["month_key", "iod"]], on="month_key", how="left")
    data = data.merge(
        mjo[["date", "mjo_phase", "mjo_amplitude", "rmm1", "rmm2"]],
        on="date",
        how="left",
    )
    data = data.drop(columns=["month_key"])
    return data


def build_location_training_rows(daily: pd.DataFrame, location: Location) -> pd.DataFrame:
    data = add_observed_features(daily)
    onset_dates = _find_agricultural_onset_dates(data)

    rain = data["rainfall_mm"].astype(float)
    rows: list[dict] = []

    # Forecast issue dates. Week 4 can extend into October.
    issue_mask = (
        ((data["date"].dt.month == 5) & (data["date"].dt.day >= 15))
        | data["date"].dt.month.isin([6, 7, 8])
        | ((data["date"].dt.month == 9) & (data["date"].dt.day <= 15))
    )

    for lead_week in (1, 2, 3, 4):
        start_offset = 1 + 7 * (lead_week - 1)
        target = _window(rain, start_offset, 7)
        target_total = target.sum(axis=1, min_count=7)
        target_wet_days = (target >= WET_DAY_MM).sum(axis=1)
        target_dry_days = (target < DRY_DAY_MM).sum(axis=1)
        target_max = target.max(axis=1)

        previous_to_target = _window(rain, start_offset - 7, 7) if start_offset >= 7 else None
        if previous_to_target is None:
            # For week 1, previous seven days are all observed by issue time.
            previous_total = data["rainfall_7d"]
        else:
            previous_total = previous_to_target.sum(axis=1, min_count=7)

        target_start_dates = data["date"] + pd.to_timedelta(start_offset, unit="D")
        target_end_dates = target_start_dates + pd.Timedelta(days=6)

        onset_target = []
        for issue_date, target_start, target_end in zip(
            data["date"], target_start_dates, target_end_dates
        ):
            onset_date = onset_dates.get(int(target_start.year))
            onset_target.append(
                int(onset_date is not None and target_start <= onset_date <= target_end)
            )

        break_target = (
            target_start_dates.dt.month.isin([6, 7, 8, 9])
            & (target_total <= 10.0)
            & (target_dry_days >= 5)
        ).astype(int)

        revival_target = (
            target_start_dates.dt.month.isin([6, 7, 8, 9])
            & (previous_total <= 10.0)
            & (target_total >= 25.0)
            & (target_wet_days >= 3)
        ).astype(int)

        heavy_target = (target_max >= HEAVY_RAIN_THRESHOLD_MM).astype(int)

        for idx in data.index[issue_mask]:
            if pd.isna(target_total.loc[idx]):
                continue
            row = {
                "date": data.loc[idx, "date"].date().isoformat(),
                "state": location.state,
                "district": location.district,
                "block": location.block,
                "panchayat": location.panchayat,
                "latitude": location.latitude,
                "longitude": location.longitude,
                "lead_week": lead_week,
                "rainfall_1d": data.loc[idx, "rainfall_1d"],
                "rainfall_3d": data.loc[idx, "rainfall_3d"],
                "rainfall_7d": data.loc[idx, "rainfall_7d"],
                "rainfall_14d": data.loc[idx, "rainfall_14d"],
                "rainfall_30d": data.loc[idx, "rainfall_30d"],
                "rainfall_anomaly_pct": data.loc[idx, "rainfall_anomaly_pct"],
                "rainy_days_7d": data.loc[idx, "rainy_days_7d"],
                "dry_days_7d": data.loc[idx, "dry_days_7d"],
                "soil_moisture": data.loc[idx, "soil_moisture"],
                "soil_moisture_7d_mean": data.loc[idx, "soil_moisture_7d_mean"],
                "humidity": data.loc[idx, "humidity"],
                "humidity_7d_mean": data.loc[idx, "humidity_7d_mean"],
                "temperature_c": data.loc[idx, "temperature_c"],
                "temperature_7d_mean": data.loc[idx, "temperature_7d_mean"],
                "wind_speed_ms": data.loc[idx, "wind_speed_ms"],
                "wind_7d_mean": data.loc[idx, "wind_7d_mean"],
                "enso": data.loc[idx, "enso"],
                "iod": data.loc[idx, "iod"],
                "mjo_phase": data.loc[idx, "mjo_phase"],
                "mjo_amplitude": data.loc[idx, "mjo_amplitude"],
                "rmm1": data.loc[idx, "rmm1"],
                "rmm2": data.loc[idx, "rmm2"],
                "onset": onset_target[idx],
                "break": int(break_target.loc[idx]),
                "revival": int(revival_target.loc[idx]),
                "heavy_rain": int(heavy_target.loc[idx]),
            }
            rows.append(row)

    result = pd.DataFrame(rows)
    numeric = result.select_dtypes(include=[np.number]).columns
    result[numeric] = result[numeric].replace([np.inf, -np.inf], np.nan)
    return result
