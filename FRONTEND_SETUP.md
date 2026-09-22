# MOSAIC Professional Frontend

Copy the `frontend/` folder contents over your existing Next.js `frontend/`.

From `MOSAIC/frontend` install the UI dependencies:

```powershell
npm install lucide-react recharts leaflet react-leaflet clsx
npm install -D @types/leaflet
```

Create `.env.local`:

```env
NEXT_PUBLIC_MOSAIC_API_URL=http://127.0.0.1:8000
```

Run backend from `MOSAIC/`:

```powershell
.\ml\.venv\Scripts\Activate.ps1
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

Run frontend in a second terminal from `MOSAIC/frontend`:

```powershell
npm run dev
```

Open http://localhost:3000

## Pages

- `/` Overview
- `/forecast`
- `/risk-map`
- `/advisory`
- `/analytics`
- `/methodology`

The dashboard intentionally labels the default form values as sample inputs.
The current backend does not yet fetch live meteorological features automatically.
