from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


LOCATIONS = [
    ("West Bengal", "Nadia", "Krishnanagar I", "Dogachhi"),
    ("West Bengal", "Nadia", "Krishnanagar II", "Noapara II"),
    ("West Bengal", "Murshidabad", "Berhampore", "Manindranagar"),
    ("Odisha", "Khordha", "Bhubaneswar", "Tamando"),
    ("Odisha", "Cuttack", "Baranga", "Kurunti"),
    ("Maharashtra", "Pune", "Haveli", "Wagholi"),
    ("Maharashtra", "Nashik", "Niphad", "Pimpalgaon"),
    ("Madhya Pradesh", "Indore", "Mhow", "Kodariya"),
]


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -20, 20)))


def sample_event(rng, probability):
    return rng.binomial(1, np.clip(probability, 0.02, 0.98))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=12000)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("ml/data/raw/mosaic_training.csv"),
    )
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    rng = np.random.default_rng(args.seed)
    dates = pd.date_range("2021-05-15", "2025-10-15", freq="D")

    records = []

    for _ in range(args.rows):
        date = pd.Timestamp(rng.choice(dates))
        state, district, block, panchayat = LOCATIONS[
            rng.integers(0, len(LOCATIONS))
        ]

        lead_week = int(rng.integers(1, 5))

        seasonal = max(
            0.0,
            np.sin((date.dayofyear - 135) / 365.25 * 2 * np.pi),
        )

        rainfall_1d = max(0.0, rng.gamma(1.5, 5.0) * seasonal)
        rainfall_3d = max(rainfall_1d, rng.gamma(2.0, 8.0) * seasonal)
        rainfall_7d = max(rainfall_3d, rng.gamma(2.5, 14.0) * seasonal)
        rainfall_14d = max(rainfall_7d, rng.gamma(3.0, 20.0) * seasonal)

        rainfall_anomaly_pct = rng.normal(0, 35)
        soil_moisture = np.clip(
            0.20 + 0.0045 * rainfall_14d + rng.normal(0, 0.10),
            0.05,
            1.0,
        )
        humidity = np.clip(55 + 30 * seasonal + rng.normal(0, 8), 25, 100)
        temperature_c = np.clip(
            36 - 7 * seasonal + rng.normal(0, 3),
            18,
            45,
        )
        wind_speed_ms = np.clip(rng.normal(4.5, 1.8), 0.2, 15)

        enso = np.clip(rng.normal(0, 0.9), -2.5, 2.5)
        iod = np.clip(rng.normal(0, 0.55), -1.5, 1.5)
        mjo_phase = int(rng.integers(1, 9))
        mjo_amplitude = np.clip(rng.gamma(2.0, 0.6), 0.1, 4.0)

        nwp_rainfall_mm = max(
            0.0,
            25
            + 85 * seasonal
            + 0.45 * rainfall_7d
            + rng.normal(0, 28)
            - 6 * (lead_week - 1),
        )
        nwp_rainfall_anomaly_pct = np.clip(
            rainfall_anomaly_pct + rng.normal(0, 25),
            -100,
            200,
        )
        nwp_ensemble_spread_mm = np.clip(
            8 + 5 * lead_week + rng.gamma(2, 4),
            2,
            80,
        )

        mjo_active = float(mjo_amplitude >= 1.0)

        onset_p = sigmoid(
            -3.0
            + 0.018 * nwp_rainfall_mm
            + 1.8 * soil_moisture
            + 0.018 * humidity
            + 0.007 * rainfall_anomaly_pct
            + 0.15 * mjo_active
            - 0.10 * (lead_week - 1)
        )

        break_p = sigmoid(
            1.0
            - 0.022 * nwp_rainfall_mm
            - 1.7 * soil_moisture
            - 0.010 * rainfall_anomaly_pct
            + 0.15 * (lead_week - 1)
            + 0.08 * abs(enso)
        )

        revival_p = sigmoid(
            -2.2
            + 0.020 * nwp_rainfall_mm
            + 0.012 * max(nwp_rainfall_anomaly_pct, 0)
            + 0.20 * mjo_active
            + 0.30 * soil_moisture
            - 0.08 * (lead_week - 1)
        )

        heavy_p = sigmoid(
            -5.0
            + 0.026 * nwp_rainfall_mm
            + 0.009 * rainfall_7d
            + 0.018 * humidity
            + 0.006 * max(nwp_rainfall_anomaly_pct, 0)
        )

        records.append(
            {
                "date": date.date().isoformat(),
                "state": state,
                "district": district,
                "block": block,
                "panchayat": panchayat,
                "lead_week": lead_week,
                "rainfall_1d": round(rainfall_1d, 3),
                "rainfall_3d": round(rainfall_3d, 3),
                "rainfall_7d": round(rainfall_7d, 3),
                "rainfall_14d": round(rainfall_14d, 3),
                "rainfall_anomaly_pct": round(rainfall_anomaly_pct, 3),
                "soil_moisture": round(float(soil_moisture), 4),
                "humidity": round(float(humidity), 3),
                "temperature_c": round(float(temperature_c), 3),
                "wind_speed_ms": round(float(wind_speed_ms), 3),
                "enso": round(float(enso), 3),
                "iod": round(float(iod), 3),
                "mjo_phase": mjo_phase,
                "mjo_amplitude": round(float(mjo_amplitude), 3),
                "nwp_rainfall_mm": round(float(nwp_rainfall_mm), 3),
                "nwp_rainfall_anomaly_pct": round(
                    float(nwp_rainfall_anomaly_pct), 3
                ),
                "nwp_ensemble_spread_mm": round(
                    float(nwp_ensemble_spread_mm), 3
                ),
                "onset": sample_event(rng, onset_p),
                "break": sample_event(rng, break_p),
                "revival": sample_event(rng, revival_p),
                "heavy_rain": sample_event(rng, heavy_p),
            }
        )

    output = args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(records).sort_values("date").to_csv(output, index=False)

    print(f"Created synthetic demo dataset: {output}")
    print(f"Rows: {len(records):,}")
    print("IMPORTANT: This dataset is only for testing the software pipeline.")


if __name__ == "__main__":
    main()
