from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(*args: str) -> None:
    command = [sys.executable, *args]
    print("\n>", " ".join(command))
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> None:
    training_csv = ROOT / "ml" / "data" / "raw" / "mosaic_training.csv"
    if not training_csv.exists():
        raise FileNotFoundError(
            "Historical dataset not found. Run first:\n"
            "python -m scripts.build_historical_dataset"
        )
    run("-m", "ml.src.preprocess", "--input", "ml/data/raw/mosaic_training.csv")
    run("-m", "ml.src.train")
    run("-m", "ml.src.evaluate")


if __name__ == "__main__":
    main()
