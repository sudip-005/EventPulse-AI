#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend")))

import asyncio
import random
import uuid
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.event import Event
from app.models.road import Road
from app.models.traffic import TrafficData
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
Session = sessionmaker(bind=engine)

def generate_roads():
    roads = []
    # Generate a simple grid network around Mumbai
    base_lat, base_lon = 19.0760, 72.8777
    for i in range(10):
        for j in range(10):
            road_id = f"road_{i}_{j}"
            from_node = f"N{i}_{j}"
            to_node = f"N{i+1}_{j}"
            road = Road(
                road_id=road_id,
                name=f"Road {i}-{j}",
                geometry=f"LINESTRING({base_lon + j*0.001} {base_lat + i*0.001}, {base_lon + j*0.001 + 0.001} {base_lat + i*0.001})",
                length_meters=100,
                speed_limit_kmh=50,
                capacity=800 + random.randint(0, 400),
                lanes=2,
                road_type="arterial",
                one_way=False,
                from_node=from_node,
                to_node=to_node
            )
            roads.append(road)
    return roads

def seed_data():
    db = Session()
    try:
        # Clear existing data (optional)
        db.query(TrafficData).delete()
        db.query(Event).delete()
        db.query(Road).delete()
        
        # Create roads
        roads = generate_roads()
        db.add_all(roads)
        db.commit()
        print(f"Added {len(roads)} roads")
        
        # Create sample event
        event = Event(
            name="Sample Concert",
            event_type="concert",
            description="A large concert event",
            location=f"POINT({72.8777 + 0.002} {19.0760 + 0.002})",
            address="Mumbai",
            estimated_attendance=15000,
            start_time=datetime.now() + timedelta(days=2, hours=18),
            end_time=datetime.now() + timedelta(days=2, hours=23),
            impact_score=75.0,
            risk_score=60.0,
            status="scheduled"
        )
        db.add(event)
        db.commit()
        print(f"Created event: {event.name} (id: {event.id})")
        
        # Generate traffic data for last 7 days
        for road in roads[:20]:  # only some roads
            for day in range(7):
                base_time = datetime.now() - timedelta(days=day)
                for hour in range(0, 24, 2):
                    ts = base_time.replace(hour=hour, minute=0, second=0)
                    speed = 40 + random.gauss(0, 10)
                    volume = 400 + random.gauss(0, 100)
                    traffic = TrafficData(
                        road_id=road.road_id,
                        timestamp=ts,
                        speed_kmh=max(10, min(80, speed)),
                        volume=max(50, volume),
                        occupancy=random.uniform(0.2, 0.8),
                        congestion_level=int(random.uniform(0, 5)),
                        weather_condition=random.choice(["clear", "cloudy", "rain"]),
                        temperature=random.uniform(20, 30),
                        precipitation=random.uniform(0, 5)
                    )
                    db.add(traffic)
        db.commit()
        print("Traffic data seeded")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()