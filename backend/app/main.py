from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.advisory import router as advisory_router
from backend.app.api.forecast import router as forecast_router
from backend.app.api.health import router as health_router
from backend.app.api.locations import router as locations_router
from backend.app.api.model_info import router as model_info_router
from backend.app.core.config import APP_NAME, APP_VERSION, CORS_ORIGINS
from backend.app.services.model_service import model_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    model_service.load()
    yield


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=(
        "FastAPI bridge between the MOSAIC Next.js frontend and the historical "
        "monsoon ML models."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(forecast_router)
app.include_router(advisory_router)
app.include_router(model_info_router)
app.include_router(locations_router)


@app.get("/")
def root() -> dict:
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "health": "/api/health",
        "predict": "/api/predict",
        "advisory": "/api/advisory",
        "model_info": "/api/model-info",
        "locations": "/api/locations",
    }
