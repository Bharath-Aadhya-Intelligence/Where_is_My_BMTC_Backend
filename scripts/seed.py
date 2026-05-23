"""Database seeding script."""

import json
import sys
from pathlib import Path

from pymongo import MongoClient

# Allow running as: python scripts/seed.py
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.config import get_settings  # noqa: E402
from app.utils.helpers import utc_now_iso  # noqa: E402


def seed_database() -> None:
    settings = get_settings()
    print(f"Connecting to MongoDB database '{settings.MONGODB_DB}'...")
    client = MongoClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_DB]
    data_dir = ROOT / "data"

    print("Dropping existing collections...")
    for name in ("buses", "stops", "routes", "live_tracking", "analytics"):
        db[name].drop()

    now = utc_now_iso()

    print("Seeding buses...")
    with open(data_dir / "buses.json") as f:
        buses = json.load(f)
    for bus in buses:
        bus.setdefault("bus_type", "standard")
        bus.setdefault("status", "active")
        bus["created_at"] = now
        bus["updated_at"] = now
    if buses:
        db["buses"].insert_many(buses)
        print(f"Successfully seeded {len(buses)} buses.")

    print("Seeding stops...")
    with open(data_dir / "stops.json") as f:
        stops = json.load(f)
    if stops:
        db["stops"].insert_many(stops)
        print(f"Successfully seeded {len(stops)} stops.")

    print("Seeding routes...")
    with open(data_dir / "routes.json") as f:
        routes = json.load(f)
    for route in routes:
        route.setdefault("direction", "up")
        if not route.get("polyline"):
            route["polyline"] = []
    if routes:
        db["routes"].insert_many(routes)
        print(f"Successfully seeded {len(routes)} routes.")

    print("Creating indexes...")
    db["buses"].create_index("bus_number", unique=True)
    db["buses"].create_index("route_id")
    db["buses"].create_index("status")
    db["routes"].create_index("route_id", unique=True)
    db["stops"].create_index([("location", "2dsphere")])
    db["stops"].create_index("stop_name")
    db["stops"].create_index("stop_id", unique=True, sparse=True)
    db["live_tracking"].create_index("bus_number")
    db["live_tracking"].create_index([("location", "2dsphere")])
    db["live_tracking"].create_index("timestamp")
    db["analytics"].create_index("event_type")
    db["analytics"].create_index("timestamp")

    print("Database seeding completed successfully.")


if __name__ == "__main__":
    seed_database()
