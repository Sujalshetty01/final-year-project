"""
FastAPI Application for Malware Classification using Graph Neural Networks
Main entry point for the ML backend service
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse

from app.routes import analysis, health
from app.routes import debug
from app.routes import evaluate
from app.model_loader import ModelLoader
from app.auth_db import init_db, create_user, get_user
from app.config import get_settings
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response, Request
import jwt
import os


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

# Simple JWT auth dependency
from fastapi.security import HTTPBearer


class JWTAuth(HTTPBearer):
    def __init__(self) -> None:
        super().__init__()

    async def __call__(self, request: Request):
        header = request.headers.get('authorization')
        if not header:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Missing authorization header')
        token = header.split(' ', 1)[-1]
        secret = os.environ.get('JWT_SECRET', 'dev-secret')
        # Enforce HTTPS in production if configured
        require_https = os.environ.get('REQUIRE_HTTPS', 'false').lower() in ('1', 'true', 'yes')
        if require_https:
            scheme = request.url.scheme
            if scheme != 'https':
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='HTTPS required')
        try:
            payload = jwt.decode(token, secret, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token expired')
        except Exception:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')

jwt_auth = JWTAuth()



@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - startup and shutdown events"""
    global model_loader
    logger.info("Starting Malware Classification API...")
    try:
        # Initialize auth DB and ensure admin user exists
        init_db()
        admin_user = os.environ.get('REVIEW_USER', 'admin')
        admin_pass = os.environ.get('REVIEW_PASS', 'admin')
        # create admin user if missing
        if get_user(admin_user) is None:
            create_user(admin_user, admin_pass)
        # Ensure models exist and start loading in background so startup is fast
        import asyncio
        async def _load_models_bg():
            try:
                await asyncio.to_thread(model_loader._ensure_models)
                logger.info("Background model loading completed")
            except Exception as e:
                logger.error(f"Background model loading failed: {e}")

        # kick off background model loading and attach task to app state
        app.state.models_loading_task = asyncio.create_task(_load_models_bg())
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
    app.state.revoked_tokens = set()
    
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
    # auth router (login)
    from app.routes import auth
    app.include_router(auth.router, prefix="/api/v1", tags=["Auth"])
    app.include_router(debug.router, prefix="/api/v1", tags=["Debug"]) 
    # evaluation router (protected)
    app.include_router(evaluate.router, prefix="/api/v1", tags=["Evaluation"], dependencies=[Depends(jwt_auth)])

    @app.get('/metrics')
    async def metrics_endpoint():
        data = generate_latest()
        return Response(content=data, media_type=CONTENT_TYPE_LATEST)

    # expose analysis result cache for evaluation route
    try:
        app.state.results_cache = analysis.results_cache
    except Exception:
        app.state.results_cache = {}
    
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
