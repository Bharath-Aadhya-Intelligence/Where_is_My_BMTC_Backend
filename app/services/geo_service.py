"""Shared geospatial utilities."""

import math
from typing import Any


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Distance in kilometers between two WGS84 points."""
    r = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    return 2 * r * math.asin(math.sqrt(a))


def geojson_point(lng: float, lat: float) -> dict[str, Any]:
    return {"type": "Point", "coordinates": [lng, lat]}


def extract_lat_lng(location: dict[str, Any]) -> tuple[float, float]:
    coords = location.get("coordinates", [0.0, 0.0])
    return coords[1], coords[0]


def eta_seconds_from_distance_km(distance_km: float, speed_kmh: float = 25.0) -> int:
    if speed_kmh <= 0:
        return 0
    hours = distance_km / speed_kmh
    return max(int(hours * 3600), 0)
