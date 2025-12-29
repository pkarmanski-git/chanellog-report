FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Kopiuje tylko kod (dzięki .dockerignore pominie modele)
COPY . .

# Te foldery zostaną nadpisane przez wolumeny przy starcie
RUN mkdir -p /app/reports /app/models

ENV APP_PORT=65000
CMD sh -c "uvicorn main:app --host 0.0.0.0 --port ${APP_PORT}"