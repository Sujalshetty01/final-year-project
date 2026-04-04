
FROM python:3.10-slim AS builder
WORKDIR /app
ENV PYTHONPATH=/app

# Install build dependencies
RUN apt-get update && apt-get install -y build-essential curl

# Install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Copy app source
COPY app ./app

# Final image
FROM python:3.10-slim
WORKDIR /app
ENV PYTHONPATH=/app

# Install runtime dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m appuser
USER appuser

# Copy installed packages and app
COPY --from=builder /app /app
COPY --chown=appuser:appuser entrypoint_backend.sh /entrypoint_backend.sh
RUN chmod +x /entrypoint_backend.sh
ENV PATH="/home/appuser/.local/bin:$PATH"

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=5 \
	CMD curl -f http://localhost:8000/api/v1/health || exit 1

ENTRYPOINT ["/entrypoint_backend.sh"]
