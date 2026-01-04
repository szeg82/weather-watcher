import streamlit as st
import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def translate_weather_code(code: int) -> str:
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

st.set_page_config(page_title="Időjárás Dashboard", layout="wide")

st.title("🌦️ Időjárás Figyelő Rendszer")

# 1. Városok lekérése az oldalsávhoz
try:
    cities_res = requests.get(f"{BACKEND_URL}/cities")
    cities = cities_res.json() if cities_res.status_code == 200 else []
except Exception:
    cities = []

# 2. Oldalsáv beállítása
st.sidebar.header("📍 Város kiválasztása")
if cities:
    city_names = [c['city_name'] for c in cities]
    selected_city_name = st.sidebar.selectbox("Város:", city_names)
    selected_city_id = next(c['id'] for c in cities if c['city_name'] == selected_city_name)

    if st.sidebar.button(f"{selected_city_name} frissítése most"):
        with st.spinner("Lekérés..."):
            requests.post(f"{BACKEND_URL}/weather/update?city_name={selected_city_name}")
            st.sidebar.success("Frissítve!")
            st.rerun()
else:
    st.sidebar.warning("Nincsenek elérhető városok.")
    selected_city_name = None
    selected_city_id = None



# 3. Statisztikák (Összesített)
st.header("📊 Statisztika")
try:
    stats_res = requests.get(f"{BACKEND_URL}/weather/stats")
    if stats_res.status_code == 200:
        stats = stats_res.json()
        col1, col2, col3 = st.columns(3)
        # Ellenőrizzük, hogy a kulcsok léteznek-e (KeyError elkerülése)
        col1.metric("Átlagos Hőmérséklet", f"{stats.get('avg_temp', 0)} °C")
        col2.metric("Mérések száma", stats.get('count', 0))
        col3.metric("Max hőmérséklet", f"{stats.get('max_temp', 0)} °C")
except Exception as e:
    st.error(f"Nem sikerült a statisztikák lekérése: {e}")

# 4. Előzmények és Vizualizáció a kiválasztott városhoz
if selected_city_id:
    st.header(f"📈 Mérési előzmények: {selected_city_name}")
    try:
        # Itt küldjük a city_id paramétert!
        history_res = requests.get(f"{BACKEND_URL}/weather/history?city_id={selected_city_id}&limit=50")
        if history_res.status_code == 200:
            data = history_res.json()
            if data:
                df = pd.DataFrame(data)
                df['időpont'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
                df['leírás'] = df['weather_code'].map(translate_weather_code)

                # Diagram (itt az eredeti oszlopnevet használjuk a tengelyhez)
                st.line_chart(df.set_index('timestamp')['temperature'])

                # Oszlopok átnevezése a megjelenítéshez
                df_display = df.rename(columns={
                    'temperature': 'Hőmérséklet (°C)',
                    'leírás': 'Állapot',
                    'cloud_cover': 'Felhőzet (%)',
                    'humidity': 'Páratartalom (%)',
                    'wind_speed': 'Szélsebesség (km/h)',
                    'apparent_temperature': 'Hőérzet (°C)',
                    'precipitation': 'Csapadék (mm)'
                })

                # Táblázat megjelenítése a magyar fejlécekkel
                st.dataframe(df_display[['időpont', 'Hőmérséklet (°C)', 'Állapot', 'Felhőzet (%)', 'Páratartalom (%)', 'Szélsebesség (km/h)']], width='stretch')
            else:
                st.info("Még nincsenek adatok ehhez a városhoz.")
    except Exception as e:
        st.error(f"Hiba az adatok megjelenítésekor: {e}")