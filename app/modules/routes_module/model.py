"""MongoDB route document shape."""

from typing import Any


def route_indexes() -> list[tuple[str, int]]:
    return [("route_id", 1)]
