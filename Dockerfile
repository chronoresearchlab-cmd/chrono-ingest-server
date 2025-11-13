# ---- Build environment ----
FROM python:3.11-slim

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app code
COPY . .

# Fly.io expects the app to listen on PORT=8080
ENV PORT=8080

EXPOSE 8080

# Start the Flask app
CMD ["python", "main.py"]
