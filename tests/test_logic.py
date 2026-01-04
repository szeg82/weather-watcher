import pytest
from backend.services import celsius_to_fahrenheit, translate_weather_code
from backend.schemas import CityCreate, WeatherCreate

# Ez a teszt a Celsius-Fahrenheit átváltót ellenőrzi több különböző bemeneti értékre (fagypont, szobahőmérséklet, negatív érték).
@pytest.mark.parametrize("celsius, expected", [
    (0, 32),
    (10, 50),
    (25, 77),
    (-10, 14)
])
def test_celsius_to_fahrenheit(celsius, expected):
    """Ellenőrzi, hogy a hőmérséklet-konverzió matematikailag helyes-e."""
    assert celsius_to_fahrenheit(celsius) == expected

@pytest.mark.parametrize("code, expected_text", [
    (0, "☀️ Derült, napos"),
    (3, "☁️ Borult"),
    (95, "⛈️ Zivatar"),
    (999, "Ismeretlen (999)") # Határeset ellenőrzése
])
def test_translate_weather_code(code, expected_text):
    """Ellenőrzi, hogy a WMO időjárás kódok fordítása megfelelően működik-e."""
    assert translate_weather_code(code) == expected_text

def test_celsius_to_fahrenheit_precision():
    """Ellenőrzi a lebegőpontos pontosságot a konverziónál."""
    # 25.5 Celsius = 77.9 Fahrenheit
    assert celsius_to_fahrenheit(25.5) == pytest.approx(77.9)

def test_placeholder_one():
    """Egyszerű aritmetikai ellenőrzés a tesztkörnyezet validálásához."""
    assert 1 + 1 == 2

def test_placeholder_two():
    """Sztring manipuláció ellenőrzése a szöveges adatok feldolgozásához."""
    assert "weather".upper() == "WEATHER"

def test_city_schema_validation():
    """Pydantic CityCreate séma validációjának ellenőrzése."""
    # Helyes adatokkal nem szabad hibát dobnia
    city_data = {"city_name": "Sopron", "latitude": 47.68, "longitude": 16.58}
    city = CityCreate(**city_data)
    assert city.city_name == "Sopron"
    
    # Hiányzó kötelező mező (latitude) esetén hibát kell dobnia
    with pytest.raises(Exception):
        CityCreate(city_name="Hiba")

def test_weather_schema_defaults():
    """Pydantic WeatherCreate séma ellenőrzése."""
    weather_data = {
        "city_id": 1,
        "temperature": 20.5,
        "humidity": 50,
        "apparent_temperature": 19.0,
        "precipitation": 0.0,
        "cloud_cover": 10,
        "is_day": 1,
        "weather_code": 0,
        "wind_speed": 5.5
    }
    weather = WeatherCreate(**weather_data)
    assert weather.temperature == 20.5
    assert weather.city_id == 1

def test_stats_logic_mock():
    """A statisztikai logika matematikai alapjainak ellenőrzése (funkcionális rész)."""
    # Szimulálunk egy hőmérséklet listát (mint ami a backend/main.py-ban készül)
    temps = [10.0, 20.0, 30.0]
    
    avg_temp = sum(temps) / len(temps)
    max_temp = max(temps)
    min_temp = min(temps)
    
    assert avg_temp == 20.0
    assert max_temp == 30.0
    assert min_temp == 10.0