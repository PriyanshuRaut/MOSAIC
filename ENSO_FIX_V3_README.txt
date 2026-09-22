MOSAIC ENSO FIX v3

Cause:
The old MOSAIC version used the PSL nina34.anom.csv path/cache. The historical
training CSV can therefore keep ENSO entirely missing even after the first parser patch.

This patch switches ENSO to NOAA/CPC detrended Nino 3.4 monthly anomalies:
https://www.cpc.ncep.noaa.gov/data/indices/detrend.nino34.ascii.txt

and uses a NEW cache filename: nino34_cpc_ersstv6.txt.

After extracting into MOSAIC root:

1. Test the source first:
   python -m scripts.test_enso_source

2. Rebuild the dataset:
   python -m scripts.build_historical_dataset

3. Check it:
   python -m scripts.check_historical_dataset

4. Only if ENSO is present, retrain:
   python -m scripts.train_all_models

The existing mosaic_training.csv is not modified just by extracting the patch.
It must be rebuilt.
