MOSAIC HISTORICAL MODEL - INSTALL/REPLACE

Copy these folders/files into the ROOT of your existing MOSAIC project and allow replacement of matching ML files.

PowerShell commands from MOSAIC root:

1) Activate your existing ML environment:
   .\ml\.venv\Scripts\Activate.ps1

2) Install one new dependency set:
   pip install -r ml\requirements.txt

3) Build REAL historical dataset (2001-2025):
   python -m scripts.build_historical_dataset

4) Check it:
   python -m scripts.check_historical_dataset

5) Train + calibrate + evaluate:
   python -m scripts.train_all_models

6) Test prediction:
   python -m ml.src.predict --input sample_prediction_historical.json

The download step can take time. Data is cached under ml/data/raw/historical, so reruns do not re-download unchanged sources.

Do NOT use generate_demo_dataset.py after switching to this historical version, or you will overwrite the real historical training CSV with synthetic data.
