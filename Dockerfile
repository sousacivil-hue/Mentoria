FROM mcr.microsoft.com/playwright/python:v1.49.0-noble

WORKDIR /app

COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend/ backend/
COPY frontend/ frontend/

WORKDIR /app/backend
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
