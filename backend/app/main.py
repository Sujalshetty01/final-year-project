"""
FastAPI Application for Malware Classification using Graph Neural Networks
Main entry point for the ML backend service
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse

from app.routes import analysis, health
from app.model_loader import ModelLoader
from app.config import get_settings


settings = get_settings()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


# Global model loader
model_loader = ModelLoader()



@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - startup and shutdown events"""
    global model_loader
    logger.info("Starting Malware Classification API...")
    try:
        # Ensure models exist and are loaded (fallback to placeholder if missing)
        model_loader._ensure_models()
        logger.info("Models loaded successfully (with fallback if needed)")
    except Exception as e:
        logger.error(f"Failed to load models: {str(e)}")
        raise
    yield
    logger.info("Shutting down Malware Classification API...")


def create_app() -> FastAPI:
    """
    Application factory - creates and configures FastAPI app
    """
    app = FastAPI(
        title="Malware Classification API",
        description="Deep Learning-based Malware Classification using Graph Neural Networks",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # Add state for model loader
    app.state.model_loader = model_loader
    app.state.limiter = limiter
    
    # CORS Configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        max_age=3600,
    )
    
    # Compression middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Rate limit error handler
    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request, exc):
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded"}
        )
    
    # Include routers
    app.include_router(health.router, prefix="/api/v1", tags=["Health"])
    app.include_router(analysis.router, prefix="/api/v1", tags=["Analysis"])
    
    return app


app = create_app()





if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level="info"
    )
