FROM python:3.10-slim
WORKDIR /app/backend

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y --no-install-recommends build-essential curl && rm -rf /var/lib/apt/lists/*


# Copy backend code into /app/backend
COPY . /app/backend

# Copy requirements.txt to /app for install step
WORKDIR /app
COPY requirements.txt ./

# Install requirements and PyTorch (CPU)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Switch back to backend as working directory
WORKDIR /app/backend

## Removed entrypoint_backend.sh logic (file not present)

# Create non-root user
RUN useradd -m appuser
RUN chown -R appuser:appuser /app
USER appuser

# Entrypoint and default command
ENTRYPOINT ["uvicorn"]
CMD ["main:app", "--host", "0.0.0.0", "--port", "8000"]

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=5 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1
