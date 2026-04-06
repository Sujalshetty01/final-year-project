FROM python:3.10-slim
WORKDIR /app

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y --no-install-recommends build-essential curl && rm -rf /var/lib/apt/lists/*

# Install Python dependencies in a separate layer for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

## Removed entrypoint_backend.sh logic (file not present)

# Create non-root user
RUN useradd -m appuser
RUN chown -R appuser:appuser /app
USER appuser

# Entrypoint and default command
ENTRYPOINT ["uvicorn"]
CMD ["app.main:app", "--host", "0.0.0.0", "--port", "8000"]

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=5 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1
