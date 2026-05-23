"""MongoDB bus document shape."""

from typing import Any


def bus_document_defaults() -> dict[str, Any]:
    return {
        "bus_type": "standard",
        "status": "active",
    }
