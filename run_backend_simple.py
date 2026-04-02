"""Start the FastAPI app in-process to avoid uvicorn's reloader for debugging."""
from backend.app.main import create_app
import uvicorn

app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")
