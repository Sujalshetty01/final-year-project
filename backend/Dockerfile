
FROM python:3.10-slim
WORKDIR /app
ENV PYTHONPATH=/app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl

# Copy requirements first for better cache
COPY requirements.txt .
COPY .env .env
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source
COPY app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
