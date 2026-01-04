import asyncio
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, database, services
from .database import engine, get_db

# Adatbázis táblák létrehozása
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Időjárás Figyelő API")


@app.get("/")
def read_root():
    return {"message": "Weather API is running"}


@app.post("/weather/update", response_model=schemas.WeatherResponse)
async def update_weather(city_name: str = "Budapest", db: Session = Depends(get_db)):
    # Megkeressük a várost az adatbázisban
    db_city = db.query(models.City).filter(models.City.city_name == city_name).first()
    if not db_city:
        # Ha nincs meg a város, megpróbáljuk alapértelmezett koordinátákkal felvenni (példa)
        raise HTTPException(status_code=404, detail=f"A(z) {city_name} város nem szerepel a listában.")
    
    data = await services.fetch_weather_data(db_city)
    if not data:
        raise HTTPException(status_code=500, detail="Sikertelen API lekérés.")

    return services.save_weather(db, schemas.WeatherCreate(**data))

@app.get("/weather/history", response_model=list[schemas.WeatherResponse])
def read_history(city_id: int = None, limit: int = 20, db: Session = Depends(get_db)):
    query = db.query(models.WeatherData)
    if city_id:
        query = query.filter(models.WeatherData.city_id == city_id)
    return query.order_by(models.WeatherData.timestamp.desc()).limit(limit).all()


@app.get("/weather/stats")
def get_stats(city_id: int = None, db: Session = Depends(get_db)):
    # Lekérdezés alapja
    query = db.query(models.WeatherData)
    
    # Ha van megadva city_id, szűrünk rá
    if city_id:
        query = query.filter(models.WeatherData.city_id == city_id)
    
    history = query.all()
    
    if not history:
        return {"avg_temp": 0, "count": 0, "max_temp": 0, "min_temp": 0}

    temps = [w.temperature for w in history]
    
    return {
        "avg_temp": round(sum(temps) / len(temps), 2),
        "count": len(history),
        "max_temp": max(temps),
        "min_temp": min(temps)
    }


@app.post("/cities", response_model=schemas.CityResponse)
def add_city(city: schemas.CityCreate, db: Session = Depends(get_db)):
    return services.create_city(db, city)

@app.get("/cities", response_model=list[schemas.CityResponse])
def list_cities(db: Session = Depends(get_db)):
    return services.get_cities(db)

# Frissített háttérfolyamat hibajavítással
@app.on_event("startup")
async def schedule_weather_updates():
    async def run_updates():
        while True:
            # Rövid várakozás, hogy a backend teljesen elinduljon
            await asyncio.sleep(5)
            db = database.SessionLocal()
            try:
                cities = services.get_cities(db)
                # Ha üres az adatbázis, adjunk hozzá egy alapértelmezettet
                if not cities:

                    default_cities = [
                        {"city_name": "Budapest", "latitude": 47.49, "longitude": 19.04},
                        {"city_name": "Debrecen", "latitude": 47.53, "longitude": 21.62},
                        {"city_name": "Szeged", "latitude": 46.25, "longitude": 20.14},
                        {"city_name": "Miskolc", "latitude": 48.10, "longitude": 20.78},
                        {"city_name": "Pécs", "latitude": 46.07, "longitude": 18.23},
                        {"city_name": "Győr", "latitude": 47.68, "longitude": 17.63},
                        {"city_name": "Nyíregyháza", "latitude": 47.95, "longitude": 21.72},
                        {"city_name": "Kecskemét", "latitude": 46.89, "longitude": 19.69},
                        {"city_name": "Székesfehérvár", "latitude": 47.19, "longitude": 18.41},
                        {"city_name": "Eger", "latitude": 47.90, "longitude": 20.37}
                    ]
                    cities = []
                    for city_data in default_cities:
                        city_schema = schemas.CityCreate(**city_data)
                        new_city = services.create_city(db, city_schema)
                        cities.append(new_city)
                
                for city in cities:
                    # Most már a city egy models.City objektum, aminek van .id attribútuma
                    data = await services.fetch_weather_data(city)
                    if data:
                        services.save_weather(db, schemas.WeatherCreate(**data))
                print(f"Sikeres frissítés: {len(cities)} város.")
            except Exception as e:
                print(f"Hiba a háttérfolyamatban: {e}")
            finally:
                db.close()
            # 10 perc várakozás a következő frissítésig
            await asyncio.sleep(600)

    asyncio.create_task(run_updates())