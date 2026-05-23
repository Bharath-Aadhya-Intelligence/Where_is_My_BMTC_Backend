import os
import json
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv()

def seed_database():
    mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    db_name = os.getenv("MONGODB_DB", "bmtc")
    print(f"Connecting to MongoDB database '{db_name}'...")
    client = MongoClient(mongo_uri)
    db = client[db_name]

    # 1. Clear existing collections
    print("Dropping existing collections...")
    db["buses"].drop()
    db["stops"].drop()
    db["routes"].drop()

    # 2. Seed buses
    print("Seeding buses...")
    with open("data/buses.json", "r") as f:
        buses = json.load(f)
    if buses:
        db["buses"].insert_many(buses)
        print(f"Successfully seeded {len(buses)} buses.")

    # 3. Seed stops
    print("Seeding stops...")
    with open("data/stops.json", "r") as f:
        stops = json.load(f)
    if stops:
        db["stops"].insert_many(stops)
        print(f"Successfully seeded {len(stops)} stops.")

    # 4. Seed routes
    print("Seeding routes...")
    with open("data/routes.json", "r") as f:
        routes = json.load(f)
    if routes:
        db["routes"].insert_many(routes)
        print(f"Successfully seeded {len(routes)} routes.")

    # 5. Create GeoSPATIAL Index
    print("Creating 2dsphere geospatial index on stops.location...")
    db["stops"].create_index([("location", "2dsphere")])
    print("Index created successfully!")

    print("Database seeding completed successfully.")

if __name__ == "__main__":
    seed_database()
