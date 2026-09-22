# MOSAIC ML

Run from the mosaic project root:

python -m venv .venv
.venv\Scripts\activate
pip install -r ml\requirements.txt

python scripts\generate_demo_dataset.py
python scripts\train_all_models.py
python -m ml.src.predict --input sample_prediction.json

IMPORTANT:
The generated demo dataset is synthetic and exists only to verify the software pipeline.
Replace ml/data/raw/mosaic_training.csv with verified meteorological/climate data before using results as scientific forecasts.
