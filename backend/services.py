import httpx
import logging
from typing import List, Dict
from . import models, schemas
from sqlalchemy.orm import Session

# Logolás beállítása
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def celsius_to_fahrenheit(celsius: float) -> float:
    """Kiszámítja a Fahrenheit értéket Celsiusból."""
    return (celsius * 9/5) + 32

def translate_weather_code(code: int) -> str:
    """A WMO (World Meteorological Organization) időjárás kódokat fordítja le magyar szövegre és emoji-ra."""
    mapping = {
        0: "☀️ Derült, napos",
        1: "🌤️ Kevés felhő",
        2: "⛅ Részben felhős",
        3: "☁️ Borult",
        45: "🌫️ Ködös",
        48: "🌫️ Zúzmarás köd",
        51: "🌧️ Szitáló eső",
        61: "🌧️ Enyhe eső",
        71: "❄️ Enyhe havazás",
        95: "⛈️ Zivatar"
    }
    return mapping.get(code, f"Ismeretlen ({code})")

async def fetch_weather_data(city: models.City) -> Dict:
    """Aszinkron módon lekéri az aktuális időjárási adatokat az Open-Meteo API-tól egy adott város koordinátái alapján."""
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={city.latitude}&longitude={city.longitude}&"
        f"current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m,cloud_cover,is_day"
    )
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()["current"]
            
            return {
                "city_id": city.id,
                "temperature": data["temperature_2m"],
                "humidity": int(data["relative_humidity_2m"]),
                "apparent_temperature": data["apparent_temperature"],
                "precipitation": data["precipitation"],
                "cloud_cover": data["cloud_cover"],
                "is_day": data["is_day"],
                "weather_code": data["weather_code"],
                "wind_speed": data["wind_speed_10m"]
            }
        except Exception as e:
            logger.error(f"Hiba {city.city_name} lekérésekor: {e}")
            return None

def get_cities(db: Session):
    """Lekéri az összes mentett várost az adatbázisból."""
    return db.query(models.City).all()

def create_city(db: Session, city: schemas.CityCreate):
    """Új várost hoz létre az adatbázisban."""
    db_city = models.City(**city.dict())
    db.add(db_city)
    db.commit()
    db.refresh(db_city)
    return db_city

# DB logika
def save_weather(db: Session, weather_data: schemas.WeatherCreate):
    """Elment egy időjárási mérési rekordot az adatbázisba."""
    db_weather = models.WeatherData(**weather_data.dict())
    db.add(db_weather)
    db.commit()
    db.refresh(db_weather)
    return db_weather

def get_history(db: Session, limit: int = 20):
    """Lekéri a legfrissebb időjárási előzményeket az adatbázisból."""
    return db.query(models.WeatherData).order_by(models.WeatherData.timestamp.desc()).limit(limit).all()