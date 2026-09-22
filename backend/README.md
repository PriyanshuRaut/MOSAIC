# MOSAIC FastAPI Backend

Run commands from the MOSAIC project root.

## Install

```powershell
.\ml\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
```

## Start

```powershell
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

Open:

- API: http://127.0.0.1:8000
- Swagger: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/api/health

The backend loads the four trained files from `ml/models/` once at startup.
