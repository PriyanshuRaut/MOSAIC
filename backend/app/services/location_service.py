from __future__ import annotations

from functools import lru_cache

import pandas as pd

from backend.app.core.config import DATASET_PATH


@lru_cache(maxsize=1)
def known_locations() -> list[dict]:
    if not DATASET_PATH.exists():
        return []

    frame = pd.read_csv(
        DATASET_PATH,
        usecols=[
            "state",
            "district",
            "block",
            "panchayat",
            "latitude",
            "longitude",
        ],
    )

    unique = (
        frame.drop_duplicates()
        .sort_values(["state", "district", "block", "panchayat"])
        .reset_index(drop=True)
    )

    return unique.to_dict(orient="records")
