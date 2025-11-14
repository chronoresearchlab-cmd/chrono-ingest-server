# ---------------------------------------------------
# ChronoNeura Ingest Server / FastAPI (Fly.io)
# ---------------------------------------------------

FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# ---- Install system deps (必要最低限) ----
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ---- Copy only requirements first（これが重要） ----
COPY requirements.txt /app/requirements.txt

# ---- Install Python deps ----
RUN pip install --no-cache-dir -r /app/requirements.txt

# ---- Copy app source ----
COPY . /app

# ---- Expose port ----
EXPOSE 8080

# ---- Start FastAPI ----
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
