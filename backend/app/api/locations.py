from __future__ import annotations

from fastapi import APIRouter

from backend.app.services.location_service import known_locations

router = APIRouter(prefix="/api", tags=["Locations"])


@router.get("/locations")
def locations() -> dict:
    items = known_locations()
    return {
        "count": len(items),
        "locations": items,
        "note": (
            "These are locations represented in the current historical baseline dataset, "
            "not the final national Panchayat coverage."
        ),
    }
