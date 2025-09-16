from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime

class PovertyAreaBase(BaseModel):
    """
    Base poverty area schema.
    """
    name: str = Field(..., max_length=200, description="Name of the poverty area")
    description: Optional[str] = Field(None, description="Detailed description of the area")
    location: Dict[str, Any] = Field(..., description="Geolocation data (lat, lng, address)")
    poverty_rate: float = Field(..., ge=0, le=100, description="Poverty rate percentage (0-100)")
    population: Optional[int] = Field(None, ge=0, description="Total population in the area")
    needs: Optional[List[str]] = Field(None, description="List of identified needs in the area")

class PovertyAreaCreate(PovertyAreaBase):
    """
    Schema for creating a new poverty area.
    """
    @validator('location')
    def validate_location(cls, v):
        required_keys = {'lat', 'lng'}
        if not required_keys.issubset(v.keys()):
            raise ValueError('Location must contain lat and lng')
        if not (-90 <= v['lat'] <= 90):
            raise ValueError('Latitude must be between -90 and 90')
        if not (-180 <= v['lng'] <= 180):
            raise ValueError('Longitude must be between -180 and 180')
        return v

class PovertyAreaUpdate(BaseModel):
    """
    Schema for updating a poverty area.
    """
    name: Optional[str] = Field(None, max_length=200, description="Name of the poverty area")
    description: Optional[str] = Field(None, description="Detailed description of the area")
    location: Optional[Dict[str, Any]] = Field(None, description="Geolocation data (lat, lng, address)")
    poverty_rate: Optional[float] = Field(None, ge=0, le=100, description="Poverty rate percentage (0-100)")
    population: Optional[int] = Field(None, ge=0, description="Total population in the area")
    needs: Optional[List[str]] = Field(None, description="List of identified needs in the area")
    
    @validator('location')
    def validate_location(cls, v):
        if v is not None:
            required_keys = {'lat', 'lng'}
            if not required_keys.issubset(v.keys()):
                raise ValueError('Location must contain lat and lng')
            if not (-90 <= v['lat'] <= 90):
                raise ValueError('Latitude must be between -90 and 90')
            if not (-180 <= v['lng'] <= 180):
                raise ValueError('Longitude must be between -180 and 180')
        return v

class PovertyAreaInDBBase(PovertyAreaBase):
    """
    Base schema for poverty area stored in DB.
    """
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class PovertyAreaResponse(PovertyAreaInDBBase):
    """
    Poverty area response schema.
    """
    pass

class PovertyAreaMapResponse(BaseModel):
    """
    Poverty area schema for map visualization.
    """
    id: int
    name: str
    location: Dict[str, Any]
    poverty_rate: float
    population: Optional[int] = None
    needs: List[str] = []
    marker_color: str = "red"
    
    class Config:
        orm_mode = True

class PovertyStatsSummary(BaseModel):
    """
    Poverty statistics summary schema.
    """
    total_areas: int = 0
    avg_poverty_rate: float = 0.0
    total_population: int = 0
    most_common_needs: List[Dict[str, Any]] = []
    poverty_distribution: List[Dict[str, Any]] = []
    
    class Config:
        orm_mode = True

class PovertyNeedsAnalysis(BaseModel):
    """
    Poverty needs analysis schema.
    """
    need: str
    count: int
    percentage: float
    areas: List[Dict[str, Any]] = []
    
    class Config:
        orm_mode = True

class PovertyAreaFilter(BaseModel):
    """
    Poverty area filter schema.
    """
    min_poverty_rate: Optional[float] = Field(None, ge=0, le=100, description="Minimum poverty rate (0-100)")
    max_poverty_rate: Optional[float] = Field(None, ge=0, le=100, description="Maximum poverty rate (0-100)")
    min_population: Optional[int] = Field(None, ge=0, description="Minimum population")
    max_population: Optional[int] = Field(None, ge=0, description="Maximum population")
    needs: Optional[List[str]] = Field(None, description="Filter by specific needs")
    bbox: Optional[List[float]] = Field(
        None, 
        min_items=4, 
        max_items=4, 
        description="Bounding box [min_lng, min_lat, max_lng, max_lat] for spatial filtering"
    )
    
    @validator('max_poverty_rate')
    def validate_poverty_rate_range(cls, v, values):
        if 'min_poverty_rate' in values and values['min_poverty_rate'] is not None and v is not None:
            if values['min_poverty_rate'] > v:
                raise ValueError('Minimum poverty rate cannot be greater than maximum poverty rate')
        return v
    
    @validator('max_population')
    def validate_population_range(cls, v, values):
        if 'min_population' in values and values['min_population'] is not None and v is not None:
            if values['min_population'] > v:
                raise ValueError('Minimum population cannot be greater than maximum population')
        return v
    
    @validator('bbox')
    def validate_bbox(cls, v):
        if v is not None:
            if len(v) != 4:
                raise ValueError('Bounding box must have exactly 4 values')
            min_lng, min_lat, max_lng, max_lat = v
            if not (-180 <= min_lng <= 180) or not (-180 <= max_lng <= 180):
                raise ValueError('Longitude values must be between -180 and 180')
            if not (-90 <= min_lat <= 90) or not (-90 <= max_lat <= 90):
                raise ValueError('Latitude values must be between -90 and 90')
            if min_lng >= max_lng or min_lat >= max_lat:
                raise ValueError('Invalid bounding box coordinates')
        return v
