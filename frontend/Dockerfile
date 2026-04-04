
# Stage 1: Build React app
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
# Debug: list build output
RUN ls -la build

# Stage 2: Serve build
FROM node:20-alpine
WORKDIR /app
RUN npm install -g http-server && apk add --no-cache curl
COPY --from=builder /app/build ./build
ENV NODE_ENV=production

# Create non-root user
RUN adduser -D appuser
USER appuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=5 \
    CMD curl -f http://localhost:8080 || exit 1
EXPOSE 8080
CMD ["http-server", "build", "-p", "8080", "--gzip", "-a", "0.0.0.0"]
