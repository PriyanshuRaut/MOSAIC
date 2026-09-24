from pathlib import Path
import json
import pandas as pd

source = Path("ml/data/raw/mosaic_training.csv")
destination = Path("backend/data/locations.json")

if not source.exists():
    raise SystemExit(f"Missing historical dataset: {source}")

columns = [
    "state",
    "district",
    "block",
    "panchayat",
    "latitude",
    "longitude",
]

frame = pd.read_csv(source, usecols=columns)
frame = (
    frame.drop_duplicates()
    .sort_values(["state", "district", "block", "panchayat"])
    .reset_index(drop=True)
)

destination.parent.mkdir(parents=True, exist_ok=True)
destination.write_text(
    json.dumps(frame.to_dict(orient="records"), indent=2, ensure_ascii=False),
    encoding="utf-8",
)

print(f"Created {destination}")
print(f"Locations: {len(frame)}")
