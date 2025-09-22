"""
Poverty map API endpoints with geospatial data
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import PovertyData, get_db

router = APIRouter()

@router.get("/data")
async def get_poverty_data(db: Session = Depends(get_db)):
    """Get poverty data for mapping"""

    poverty_data = db.query(PovertyData).all()

    return poverty_data

@router.get("/summary")
async def get_poverty_summary(db: Session = Depends(get_db)):
    """Get poverty statistics summary"""

    data = db.query(PovertyData).all()

    if not data:
        return {
            "total_regions": 0,
            "average_poverty_rate": 0,
            "highest_poverty_region": None,
            "lowest_poverty_region": None
        }

    total_poverty = sum(d.poverty_rate for d in data)
    total_population = sum(d.population for d in data)

    highest_poverty = max(data, key=lambda x: x.poverty_rate)
    lowest_poverty = min(data, key=lambda x: x.poverty_rate)

    return {
        "total_regions": len(data),
        "average_poverty_rate": total_poverty / len(data),
        "total_population": total_population,
        "highest_poverty_region": {
            "region": highest_poverty.region,
            "poverty_rate": highest_poverty.poverty_rate
        },
        "lowest_poverty_region": {
            "region": lowest_poverty.region,
            "poverty_rate": lowest_poverty.poverty_rate
        }
    }

@router.get("/regions/{region_name}")
async def get_region_data(region_name: str, db: Session = Depends(get_db)):
    """Get detailed data for a specific region"""

    region = db.query(PovertyData).filter(
        PovertyData.region.ilike(f"%{region_name}%")
    ).first()

    if not region:
        return {"error": "Region not found"}

    return region

# Sample data seeding function
def seed_poverty_data():
    """Seed database with sample poverty data"""
    from app.database import SessionLocal

    db = SessionLocal()
    try:
        # Check if data already exists
        existing_data = db.query(PovertyData).first()
        if existing_data:
            return

        sample_data = [
            {
                "region": "Downtown District",
                "latitude": 40.7128,
                "longitude": -74.0060,
                "poverty_rate": 18.5,
                "population": 150000,
                "average_income": 32000,
                "unemployment_rate": 12.3
            },
            {
                "region": "Westside Neighborhood",
                "latitude": 40.7589,
                "longitude": -73.9851,
                "poverty_rate": 25.7,
                "population": 85000,
                "average_income": 28000,
                "unemployment_rate": 15.8
            },
            {
                "region": "East End Community",
                "latitude": 40.7282,
                "longitude": -73.7949,
                "poverty_rate": 15.2,
                "population": 120000,
                "average_income": 35000,
                "unemployment_rate": 9.7
            },
            {
                "region": "South Bronx Area",
                "latitude": 40.8448,
                "longitude": -73.8648,
                "poverty_rate": 32.1,
                "population": 95000,
                "average_income": 25000,
                "unemployment_rate": 18.9
            },
            {
                "region": "Northern Suburbs",
                "latitude": 40.7831,
                "longitude": -73.9712,
                "poverty_rate": 8.9,
                "population": 200000,
                "average_income": 45000,
                "unemployment_rate": 6.2
            }
        ]

        for data in sample_data:
            poverty_record = PovertyData(**data)
            db.add(poverty_record)

        db.commit()
        print("Sample poverty data seeded successfully")
    finally:
        db.close()
