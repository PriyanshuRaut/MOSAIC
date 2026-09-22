from __future__ import annotations

import io
import json
import re
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

NASA_POWER_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
NINO34_URL = "https://www.cpc.ncep.noaa.gov/data/indices/detrend.nino34.ascii.txt"
DMI_URL = "https://psl.noaa.gov/data/timeseries/month/data/dmi.had.long.csv"
MJO_URL = "https://www.bom.gov.au/clim_data/IDCKGEM000/rmm.74toRealtime.txt"

POWER_PARAMETERS = ["PRECTOTCORR", "T2M", "RH2M", "WS2M", "GWETROOT"]
MISSING_SENTINELS = {-999.0, -9999.0, 999.0, 9999.0, 1e36}


def make_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=5,
        connect=5,
        read=5,
        backoff_factor=1.0,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET"]),
    )
    session.mount("https://", HTTPAdapter(max_retries=retry))
    session.headers.update({"User-Agent": "MOSAIC-historical-model/1.0"})
    return session


def _read_or_download_text(url: str, cache_path: Path, session: requests.Session) -> str:
    if cache_path.exists():
        return cache_path.read_text(encoding="utf-8", errors="replace")

    response = session.get(url, timeout=120)
    response.raise_for_status()
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(response.text, encoding="utf-8")
    return response.text


def _coerce_value(value):
    try:
        v = float(value)
    except (TypeError, ValueError):
        return np.nan
    if not np.isfinite(v) or any(abs(v - s) < 1e-6 for s in MISSING_SENTINELS):
        return np.nan
    if abs(v) > 1e20:
        return np.nan
    return v


def download_power_daily(
    latitude: float,
    longitude: float,
    start: str,
    end: str,
    cache_path: Path,
    session: requests.Session | None = None,
) -> pd.DataFrame:
    """Download one NASA POWER grid point for the full requested period."""
    session = session or make_session()

    if cache_path.exists():
        payload = json.loads(cache_path.read_text(encoding="utf-8"))
    else:
        params = {
            "parameters": ",".join(POWER_PARAMETERS),
            "community": "AG",
            "longitude": longitude,
            "latitude": latitude,
            "start": start.replace("-", ""),
            "end": end.replace("-", ""),
            "format": "JSON",
            "time-standard": "UTC",
        }
        response = session.get(NASA_POWER_URL, params=params, timeout=180)
        response.raise_for_status()
        payload = response.json()
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(payload), encoding="utf-8")

    try:
        parameters = payload["properties"]["parameter"]
    except KeyError as exc:
        raise RuntimeError(f"Unexpected NASA POWER response in {cache_path}") from exc

    all_dates: set[str] = set()
    for values in parameters.values():
        all_dates.update(values.keys())

    rows = []
    for date_key in sorted(all_dates):
        row = {"date": pd.to_datetime(date_key, format="%Y%m%d", errors="coerce")}
        for parameter in POWER_PARAMETERS:
            row[parameter] = _coerce_value(parameters.get(parameter, {}).get(date_key))
        rows.append(row)

    frame = pd.DataFrame(rows).dropna(subset=["date"]).sort_values("date")
    frame = frame.rename(
        columns={
            "PRECTOTCORR": "rainfall_mm",
            "T2M": "temperature_c",
            "RH2M": "humidity",
            "WS2M": "wind_speed_ms",
            "GWETROOT": "soil_moisture",
        }
    )
    frame["rainfall_mm"] = frame["rainfall_mm"].clip(lower=0)
    return frame.reset_index(drop=True)



def _parse_monthly_date_series(series: pd.Series) -> pd.Series:
    """
    Robust parser for monthly index date columns.

    Handles common NOAA/PSL forms such as:
      195001
      19500101
      1950-01
      1950-01-01
      1950/01
    including numeric columns that pandas would otherwise interpret as
    nanoseconds since 1970.
    """
    raw = series.astype("string").str.strip()
    raw = raw.str.replace(r"\.0$", "", regex=True)

    parsed = pd.Series(pd.NaT, index=series.index, dtype="datetime64[ns]")

    formats = [
        (r"^\d{6}$", "%Y%m"),
        (r"^\d{8}$", "%Y%m%d"),
        (r"^\d{4}-\d{2}$", "%Y-%m"),
        (r"^\d{4}-\d{2}-\d{2}$", "%Y-%m-%d"),
        (r"^\d{4}/\d{2}$", "%Y/%m"),
        (r"^\d{4}/\d{2}/\d{2}$", "%Y/%m/%d"),
    ]

    for pattern, fmt in formats:
        mask = parsed.isna() & raw.str.match(pattern, na=False)
        if mask.any():
            parsed.loc[mask] = pd.to_datetime(
                raw.loc[mask], format=fmt, errors="coerce"
            )

    remaining = parsed.isna()
    if remaining.any():
        parsed.loc[remaining] = pd.to_datetime(
            raw.loc[remaining], errors="coerce"
        )

    return parsed


def _parse_date_value_frame(frame: pd.DataFrame, value_name: str) -> pd.DataFrame | None:
    if frame.empty or frame.shape[1] < 2:
        return None

    columns = list(frame.columns)
    lowered = {c: str(c).strip().lower() for c in columns}

    # Explicit year + month columns.
    year_col = next((c for c in columns if lowered[c] in {"year", "yr"}), None)
    month_col = next((c for c in columns if lowered[c] in {"month", "mon", "mn"}), None)
    if year_col is not None and month_col is not None:
        numeric_candidates = [c for c in columns if c not in {year_col, month_col}]
        if numeric_candidates:
            value_col = numeric_candidates[-1]
            out = pd.DataFrame(
                {
                    "date": pd.to_datetime(
                        dict(
                            year=pd.to_numeric(frame[year_col], errors="coerce"),
                            month=pd.to_numeric(frame[month_col], errors="coerce"),
                            day=1,
                        ),
                        errors="coerce",
                    ),
                    value_name: pd.to_numeric(frame[value_col], errors="coerce"),
                }
            )
            return out.dropna(subset=["date", value_name])

    # One date-like column + one numeric value column.
    date_candidates = [
        c for c in columns if any(token in lowered[c] for token in ("date", "time"))
    ]
    date_candidates += [columns[0]]
    seen = set()
    for date_col in date_candidates:
        if date_col in seen:
            continue
        seen.add(date_col)
        parsed = _parse_monthly_date_series(frame[date_col])
        if parsed.notna().mean() < 0.7:
            continue
        numeric_candidates = [c for c in columns if c != date_col]
        for value_col in reversed(numeric_candidates):
            values = pd.to_numeric(frame[value_col], errors="coerce")
            if values.notna().mean() >= 0.5:
                out = pd.DataFrame({"date": parsed, value_name: values})
                return out.dropna(subset=["date", value_name])

    return None


def parse_psl_monthly_csv(text: str, value_name: str) -> pd.DataFrame:
    """Parse NOAA PSL monthly CSVs in either long or year-by-month layout."""
    cleaned_lines = [
        line for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith(("#", "%"))
    ]
    cleaned = "\n".join(cleaned_lines)
    frame = pd.read_csv(io.StringIO(cleaned))
    frame.columns = [str(c).strip() for c in frame.columns]

    parsed = _parse_date_value_frame(frame, value_name)
    if parsed is not None and not parsed.empty:
        parsed["date"] = parsed["date"].dt.to_period("M").dt.to_timestamp()
        return parsed.sort_values("date").drop_duplicates("date", keep="last")

    # Wide layout: Year, Jan, Feb, ... Dec
    month_map = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
        "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
    }
    columns = list(frame.columns)
    year_col = next(
        (c for c in columns if str(c).strip().lower() in {"year", "yr"}),
        columns[0] if columns else None,
    )
    month_columns = {
        c: month_map[str(c).strip().lower()[:3]]
        for c in columns
        if str(c).strip().lower()[:3] in month_map
    }
    if year_col is not None and len(month_columns) >= 10:
        rows = []
        for _, row in frame.iterrows():
            year = pd.to_numeric(row[year_col], errors="coerce")
            if pd.isna(year):
                continue
            for col, month in month_columns.items():
                value = pd.to_numeric(row[col], errors="coerce")
                if pd.notna(value) and abs(float(value)) < 100:
                    rows.append(
                        {"date": pd.Timestamp(int(year), month, 1), value_name: float(value)}
                    )
        if rows:
            return pd.DataFrame(rows).sort_values("date").drop_duplicates("date", keep="last")

    raise ValueError(f"Could not parse NOAA monthly index CSV for {value_name}.")


def parse_cpc_nino34_ascii(text: str) -> pd.DataFrame:
    """Parse NOAA/CPC monthly Nino 3.4 anomaly text.

    Expected columns:
        YR MON TOTAL ClimAdjust ANOM

    We use ANOM as the ENSO/Nino 3.4 feature.
    """
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.upper().startswith("YR"):
            continue
        parts = re.split(r"\s+", line)
        if len(parts) < 5:
            continue
        try:
            year = int(parts[0])
            month = int(parts[1])
            anomaly = float(parts[4])
        except (ValueError, TypeError):
            continue
        if not (1 <= month <= 12) or not np.isfinite(anomaly):
            continue
        rows.append({"date": pd.Timestamp(year, month, 1), "enso": anomaly})

    if not rows:
        raise ValueError("No valid NOAA/CPC Nino 3.4 rows were parsed.")

    return (
        pd.DataFrame(rows)
        .sort_values("date")
        .drop_duplicates("date", keep="last")
        .reset_index(drop=True)
    )


def download_monthly_indices(cache_dir: Path, session: requests.Session | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    session = session or make_session()
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Use a distinct cache filename so stale nina34.anom.csv files from
    # previous MOSAIC versions cannot be reused accidentally.
    nino_text = _read_or_download_text(
        NINO34_URL, cache_dir / "nino34_cpc_ersstv6.txt", session
    )
    dmi_text = _read_or_download_text(DMI_URL, cache_dir / "dmi.csv", session)

    enso = parse_cpc_nino34_ascii(nino_text)
    iod = parse_psl_monthly_csv(dmi_text, "iod")
    return enso, iod


def parse_bom_mjo(text: str) -> pd.DataFrame:
    rows = []
    for line in text.splitlines():
        parts = re.split(r"\s+", line.strip())
        if len(parts) < 7 or not parts[0].isdigit():
            continue
        try:
            year, month, day = map(int, parts[:3])
            rmm1 = float(parts[3])
            rmm2 = float(parts[4])
            phase = int(float(parts[5]))
            amplitude = float(parts[6])
        except ValueError:
            continue
        if abs(rmm1) > 100 or abs(rmm2) > 100 or amplitude > 100:
            continue
        rows.append(
            {
                "date": pd.Timestamp(year, month, day),
                "rmm1": rmm1,
                "rmm2": rmm2,
                "mjo_phase": phase,
                "mjo_amplitude": amplitude,
            }
        )
    if not rows:
        raise ValueError("No valid MJO rows were found in the BOM RMM file.")
    return pd.DataFrame(rows).sort_values("date").drop_duplicates("date", keep="last")


def download_mjo(cache_dir: Path, session: requests.Session | None = None) -> pd.DataFrame:
    session = session or make_session()
    cache_dir.mkdir(parents=True, exist_ok=True)
    text = _read_or_download_text(MJO_URL, cache_dir / "rmm.74toRealtime.txt", session)
    return parse_bom_mjo(text)
