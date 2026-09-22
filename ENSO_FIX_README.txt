MOSAIC ENSO FIX PATCH

Replace these files in your existing MOSAIC project:
- ml/src/data_sources.py
- ml/src/preprocess.py
- scripts/build_historical_dataset.py
- scripts/check_historical_dataset.py

Then, from the MOSAIC root:

1) Rebuild the historical dataset:
   python -m scripts.build_historical_dataset

2) Verify coverage:
   python -m scripts.check_historical_dataset

ENSO must NOT show 100% missing.

3) Retrain:
   python -m scripts.train_all_models

The patch also makes the pipeline fail fast if a critical climate feature is
completely missing, instead of silently training without it.
