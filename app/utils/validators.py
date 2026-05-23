"""Geo and input validators."""

import re

from app.core.exceptions import ValidationException

# Bengaluru approximate bounding box
BENGALURU_LAT_MIN = 12.75
BENGALURU_LAT_MAX = 13.25
BENGALURU_LNG_MIN = 77.35
BENGALURU_LNG_MAX = 77.85

BUS_NUMBER_PATTERN = re.compile(r"^[A-Za-z0-9\-]+$")


def validate_coordinates(lat: float, lng: float, *, strict_bbox: bool = False) -> None:
    if not (-90 <= lat <= 90):
        raise ValidationException("Latitude must be between -90 and 90")
    if not (-180 <= lng <= 180):
        raise ValidationException("Longitude must be between -180 and 180")
    if strict_bbox:
        if not (BENGALURU_LAT_MIN <= lat <= BENGALURU_LAT_MAX):
            raise ValidationException("Latitude is outside Bengaluru service area")
        if not (BENGALURU_LNG_MIN <= lng <= BENGALURU_LNG_MAX):
            raise ValidationException("Longitude is outside Bengaluru service area")


def validate_bus_number(bus_number: str) -> None:
    if not bus_number or not BUS_NUMBER_PATTERN.match(bus_number):
        raise ValidationException("Invalid bus number format")


def validate_radius(radius_m: float, *, max_m: float = 5000) -> None:
    if radius_m <= 0:
        raise ValidationException("Radius must be positive")
    if radius_m > max_m:
        raise ValidationException(f"Radius cannot exceed {max_m} meters")
