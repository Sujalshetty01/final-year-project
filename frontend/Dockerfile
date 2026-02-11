FROM node:20-alpine

WORKDIR /app

# Install simple-http-server for static files
RUN npm install -g http-server

# Copy frontend files
COPY frontend/public .

# Set environment variables
ENV NODE_ENV=production

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:8080 || exit 1

# Expose port
EXPOSE 8080

# Serve frontend
CMD ["http-server", ".", "-p", "8080", "--gzip", "-a", "0.0.0.0"]
