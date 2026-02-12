# Minimal Dockerfile for the backend service
FROM python:3.10-slim

WORKDIR /app

# Install system deps for onnxruntime and common packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY . /app

# Install backend requirements
RUN pip install --no-cache-dir -r backend/requirements.txt

# Expose server port
EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
