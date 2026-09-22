# MOSAIC

MOSAIC is a monorepo scaffold for monsoon forecasting, climate analytics, and
agricultural advisories.

## Workspaces

- `frontend/` - Next.js web application
- `backend/` - FastAPI production API
- `ml/` - data preparation, training, evaluation, and inference
- `shared/` - geographic data and sample contracts
- `scripts/` - data and model automation
- `docs/` - architecture, model, datasets, and API documentation

## Getting started

```powershell
cd frontend
npm install
npm run dev
```

To run the API after installing `backend/requirements.txt`:

```powershell
uvicorn app.main:app --reload --app-dir backend
```