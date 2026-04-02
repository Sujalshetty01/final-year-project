# Dockerfile for full-stack project
FROM python:3.10-slim AS backend
WORKDIR /app/backend
COPY backend/ ./
RUN pip install --no-cache-dir -r requirements.txt

FROM node:18-alpine AS frontend
WORKDIR /app/frontend
COPY frontend/ ./
RUN npm install && npm run build

FROM python:3.10-slim
WORKDIR /app
COPY --from=backend /app/backend ./backend
COPY --from=frontend /app/frontend/build ./frontend/build
EXPOSE 8000
CMD ["python", "backend/main.py"]