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

else:
    st.sidebar.warning("Nincsenek elérhető városok.")
    selected_city_name = None
    selected_city_id = None

# --- ÚJ VÁROS HOZZÁADÁSA ---
st.sidebar.markdown("---")
with st.sidebar.expander("➕ Új város hozzáadása"):
    new_city = st.text_input("Város neve (pl. Sopron)")
    new_lat = st.number_input("Szélesség (Latitude)", value=47.0, format="%.4f")
    new_lon = st.number_input("Hosszúság (Longitude)", value=19.0, format="%.4f")

    if st.button("Mentés"):
        if new_city:
            try:
                payload = {"city_name": new_city, "latitude": new_lat, "longitude": new_lon}
                add_res = requests.post(f"{BACKEND_URL}/cities", json=payload)
                if add_res.status_code == 200:
                    st.sidebar.success(f"{new_city} hozzáadva!")
                    st.rerun()
                else:
                    st.sidebar.error("Hiba történt a mentéskor.")
            except Exception as e:
                st.sidebar.error(f"Hiba: {e}")
        else:
            st.sidebar.warning("Kérlek add meg a város nevét!")
# ---------------------------

# 3. Statisztikák és Előzmények (csak ha van kiválasztott város)
if selected_city_id:
    # --- STATISZTIKA SZEKCIÓ ---
    st.header(f"📊 Statisztika: {selected_city_name}")
    try:
        # Itt küldjük a city_id-t a backendnek!
        stats_res = requests.get(f"{BACKEND_URL}/weather/stats?city_id={selected_city_id}")
        if stats_res.status_code == 200:
            stats = stats_res.json()
            col1, col2, col3 = st.columns(3)
            col1.metric("Átlagos Hőmérséklet", f"{stats.get('avg_temp', 0)} °C")
            col2.metric("Mérések száma", stats.get('count', 0))
            col3.metric("Max hőmérséklet", f"{stats.get('max_temp', 0)} °C")
    except Exception as e:
        st.error(f"Nem sikerült a statisztikák lekérése: {e}")

st.markdown("---")

# 4. Előzmények és Vizualizáció a kiválasztott városhoz
if selected_city_id:
    header_col, btn_col = st.columns([3, 1])
    with header_col:
        st.header(f"📈 Mérési előzmények: {selected_city_name}")
    with btn_col:
        st.write("")  # Térköz az igazításhoz
        if st.button("🔄 Adatok frissítése", use_container_width=True):
            with st.spinner("Lekérés..."):
                try:
                    res = requests.post(f"{BACKEND_URL}/weather/update?city_name={selected_city_name}")
                    if res.status_code == 200:
                        st.rerun()
                    else:
                        st.error("Sikertelen frissítés.")
                except Exception as e:
                    st.error(f"Hiba: {e}")
    # Limit kiválasztása
    limit_options = [10, 25, 50, 100]
    selected_limit = st.selectbox("Megjelenített rekordok száma:", limit_options, index=2)

    try:
        history_res = requests.get(f"{BACKEND_URL}/weather/history?city_id={selected_city_id}&limit={selected_limit}")
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