
# Setup Guide

## Prerequisites
- Node.js (for frontend)
- Python 3.8+ (for backend)
- Docker & Docker Compose (optional, for containerized setup)

---

## Local Development

### 1. Clone the repository
```sh
git clone <repo-url>
cd <repo-folder>
```

### 2. Install dependencies
- Frontend:
  ```sh
  cd frontend
  npm install
  ```
- Backend:
  ```sh
  cd backend
  pip install -r requirements.txt
  ```

### 3. Run the project
- Frontend:
  ```sh
  npm start
  ```
- Backend:
  ```sh
  python main.py
  ```

---

## One-Command Docker Deployment

To build and run both frontend and backend with Docker Compose:

```sh
docker-compose -f docker/docker-compose.yml up --build
```

This will start all services. Access the frontend at http://localhost:3000 and the backend API at http://localhost:8000.

---

## Troubleshooting
- Ensure all dependencies are installed.
- For Docker, verify Docker Desktop is running.
- Check logs for errors and consult the README for more info.

---

## More
See [../README.md](../README.md) for project overview and documentation links.