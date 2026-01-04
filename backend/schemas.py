from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class WeatherBase(BaseModel):
    temperature: float
    humidity: int
    apparent_temperature: float
    precipitation: float
    cloud_cover: int
    is_day: int
    weather_code: int
    wind_speed: float

class CityBase(BaseModel):
    city_name: str
    latitude: float
    longitude: float

class CityCreate(CityBase):
    pass

class CityResponse(CityBase):
    id: int
    class Config:
        from_attributes = True

class WeatherCreate(WeatherBase):
    city_id: int

class WeatherResponse(WeatherBase):
    id: int
    city_id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True