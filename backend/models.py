from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    city_name = Column(String, unique=True, index=True)
    latitude = Column(Float)
    longitude = Column(Float)

    # Kapcsolat az időjárási adatokkal
    weather_records = relationship("WeatherData", back_populates="city_rel")

class WeatherData(Base):
    __tablename__ = "weather_history"

    id = Column(Integer, primary_key=True, index=True)
    city_id = Column(Integer, ForeignKey("cities.id"))
    temperature = Column(Float)
    humidity = Column(Integer)
    apparent_temperature = Column(Float)
    precipitation = Column(Float) # csapadék
    cloud_cover = Column(Integer)  #  felhőzetk (%)
    is_day = Column(Integer)  # (1 = nappal, 0 = éjjel)
    weather_code = Column(Integer)
    wind_speed = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

    city_rel = relationship("City", back_populates="weather_records")