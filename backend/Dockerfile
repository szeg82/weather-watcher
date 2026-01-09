FROM python:3.9-slim

WORKDIR /app

# Függőségek másolása és telepítése
COPY requirements-backend.txt .
RUN pip install --no-cache-dir -r requirements-backend.txt

# Teljes projekt másolása
COPY . .

# A FastAPI backend elindítása uvicorn-nal
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]