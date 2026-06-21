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
from app.models.risk_assessment import RiskAssessment
from app.core.config import settings

db_url = settings.DATABASE_URL
if not db_url:
    db_url = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}/{settings.POSTGRES_DB}"

engine = create_engine(db_url)
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
                geometry={"type": "LineString", "coordinates": [[base_lon + j*0.001, base_lat + i*0.001], [base_lon + j*0.001 + 0.001, base_lat + i*0.001]]},
                length_meters=100.0,
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
        db.query(RiskAssessment).delete()
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
            location={"type": "Point", "coordinates": [72.8797, 19.0780]},
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
        
        # Create sample risk assessment
        assessment = RiskAssessment(
            event_id=event.id,
            impact_score=75.0,
            impact_level="HIGH",
            risk_score=60.0,
            expected_duration_minutes=300.0,
            closure_probability=0.3,
            top_factor_1="estimated_attendance",
            top_factor_2="priority_encoded",
            top_factor_3="is_rush_hour",
            model_version="v1.0"
        )
        db.add(assessment)
        db.commit()
        print("Risk assessment seeded")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
