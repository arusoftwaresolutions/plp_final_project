from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User, PovertyHotspot, FamilyProfile
from schemas import PovertyHotspot as PovertyHotspotSchema
from auth import get_current_user
from typing import List
import folium
import json
import io
import base64

router = APIRouter()

@router.get("/poverty-hotspots", response_model=List[PovertyHotspotSchema])
def get_poverty_hotspots(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    hotspots = db.query(PovertyHotspot).offset(skip).limit(limit).all()
    return hotspots

@router.post("/poverty-hotspots", response_model=PovertyHotspotSchema)
def create_poverty_hotspot(
    hotspot: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.user_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can create poverty hotspots"
        )
    
    db_hotspot = PovertyHotspot(**hotspot)
    db.add(db_hotspot)
    db.commit()
    db.refresh(db_hotspot)
    
    return db_hotspot

@router.get("/map")
def get_map_data(
    db: Session = Depends(get_db)
):
    """Generate map data with poverty hotspots and family locations"""
    # Get poverty hotspots
    hotspots = db.query(PovertyHotspot).all()
    
    # Get family locations
    families = db.query(FamilyProfile).filter(
        FamilyProfile.latitude.isnot(None),
        FamilyProfile.longitude.isnot(None)
    ).all()
    
    # Create map
    if hotspots:
        # Use first hotspot as center, or default to NYC
        center_lat = hotspots[0].latitude
        center_lon = hotspots[0].longitude
    else:
        center_lat, center_lon = 40.7128, -74.0060  # NYC default
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=10)
    
    # Add poverty hotspots
    for hotspot in hotspots:
        folium.CircleMarker(
            location=[hotspot.latitude, hotspot.longitude],
            radius=hotspot.poverty_rate * 10,  # Scale radius by poverty rate
            popup=f"<b>{hotspot.name}</b><br>Poverty Rate: {hotspot.poverty_rate:.1f}%<br>Population: {hotspot.population:,}",
            color='red',
            fill=True,
            fillColor='red',
            fillOpacity=0.6
        ).add_to(m)
    
    # Add family locations
    for family in families:
        folium.Marker(
            location=[family.latitude, family.longitude],
            popup=f"<b>Family</b><br>Size: {family.family_size}<br>Income: ${family.monthly_income:,.2f}/month",
            icon=folium.Icon(color='blue', icon='home')
        ).add_to(m)
    
    # Convert map to HTML string
    map_html = m._repr_html_()
    
    return {
        "map_html": map_html,
        "hotspots_count": len(hotspots),
        "families_count": len(families)
    }

@router.get("/families-near-hotspot/{hotspot_id}")
def get_families_near_hotspot(
    hotspot_id: str,
    radius_km: float = 10.0,
    db: Session = Depends(get_db)
):
    """Get families within a certain radius of a poverty hotspot"""
    hotspot = db.query(PovertyHotspot).filter(PovertyHotspot.id == hotspot_id).first()
    if not hotspot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Poverty hotspot not found"
        )
    
    # Get all families with coordinates
    families = db.query(FamilyProfile).filter(
        FamilyProfile.latitude.isnot(None),
        FamilyProfile.longitude.isnot(None)
    ).all()
    
    # Simple distance calculation (not precise for large distances)
    nearby_families = []
    for family in families:
        # Rough distance calculation (1 degree ≈ 111 km)
        lat_diff = abs(family.latitude - hotspot.latitude)
        lon_diff = abs(family.longitude - hotspot.longitude)
        distance = ((lat_diff ** 2 + lon_diff ** 2) ** 0.5) * 111
        
        if distance <= radius_km:
            nearby_families.append({
                "id": family.id,
                "latitude": family.latitude,
                "longitude": family.longitude,
                "family_size": family.family_size,
                "monthly_income": family.monthly_income,
                "distance_km": round(distance, 2)
            })
    
    return {
        "hotspot": {
            "id": hotspot.id,
            "name": hotspot.name,
            "latitude": hotspot.latitude,
            "longitude": hotspot.longitude,
            "poverty_rate": hotspot.poverty_rate
        },
        "nearby_families": nearby_families,
        "count": len(nearby_families)
    }

@router.get("/statistics")
def get_geospatial_statistics(
    db: Session = Depends(get_db)
):
    """Get geospatial statistics"""
    total_hotspots = db.query(PovertyHotspot).count()
    total_families = db.query(FamilyProfile).count()
    families_with_location = db.query(FamilyProfile).filter(
        FamilyProfile.latitude.isnot(None),
        FamilyProfile.longitude.isnot(None)
    ).count()
    
    # Calculate average poverty rate
    hotspots = db.query(PovertyHotspot).all()
    avg_poverty_rate = sum(h.poverty_rate for h in hotspots) / len(hotspots) if hotspots else 0
    
    return {
        "total_poverty_hotspots": total_hotspots,
        "total_families": total_families,
        "families_with_location": families_with_location,
        "average_poverty_rate": round(avg_poverty_rate, 2),
        "location_coverage": round((families_with_location / total_families * 100), 2) if total_families > 0 else 0
    }
