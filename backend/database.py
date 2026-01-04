import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv() # .env fájl betöltése

# Ha nincs megadva DATABASE_URL akkor automatikusan SQLite-ot használ
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./weather.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()