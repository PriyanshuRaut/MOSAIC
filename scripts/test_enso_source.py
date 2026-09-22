from pathlib import Path

from ml.src.data_sources import download_monthly_indices, make_session


def main():
    cache = Path("ml/data/raw/historical/indices")
    enso, iod = download_monthly_indices(cache, make_session())

    print("ENSO rows:", len(enso))
    print("ENSO range:", enso["date"].min(), "->", enso["date"].max())
    print("ENSO missing:", int(enso["enso"].isna().sum()))
    print("\nENSO tail:")
    print(enso.tail(12).to_string(index=False))

    print("\nIOD rows:", len(iod))
    print("IOD range:", iod["date"].min(), "->", iod["date"].max())

    required = enso[(enso["date"] >= "2001-01-01") & (enso["date"] <= "2025-12-01")]
    if required.empty or required["enso"].isna().any():
        raise SystemExit("ERROR: ENSO source coverage for 2001-2025 is incomplete.")

    print("\nENSO source check: PASS")


if __name__ == "__main__":
    main()
