# Időjárás Figyelő Rendszer – Multi-paradigmás programozás

Ez a projekt egy modern webes alkalmazás, amely szétválasztott architektúrát használ:
- **Backend:** FastAPI, SQLAlchemy (SQLite), REST API.
- **Frontend:** Streamlit.

## Funkciók
- **Adatgyűjtés:** Open-Meteo API (Aszinkron).
- **Adattárolás:** SQLite adatbázis.
- **Megjelenítés:** Interaktív Dashboard (Streamlit).
- **Automatizálás:** Háttérfolyamat az adatfrissítéshez.

## Programozási paradigmák megjelenése
- **Objektumorientált (OOP):** SQLAlchemy modellek (`City`, `WeatherData`) és Pydantic sémák használata.
- **Funkcionális:** Tiszta függvények a `services.py`-ban (pl. hőmérséklet konverzió, WMO kód fordítás), list comprehension-ök a statisztikai modulban.
- **Procedurális:** A rendszer indítása, a háttérfolyamat vezérlési szerkezete és a `main.py` indító script.

## Telepítés és futtatás

1. **Virtuális környezet létrehozása és aktiválása:**
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   ```

2. **Függőségek telepítése:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Alkalmazás indítása:**
   A gyökérkönyvtárban található `main.py` egyszerre indítja el a backendet és a frontendet:
   ```bash
   python main.py
   ```

4. **Tesztelés:**
   ```bash
   python -m pytest
   ```

## Elérhetőség
- **Backend API:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Frontend Dashboard:** [http://localhost:8501](http://localhost:8501)
