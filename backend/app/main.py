import os
from app.rbac import require_role
import sentry_sdk
SENTRY_DSN = os.getenv("SENTRY_DSN")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        traces_sample_rate=0.1,
        environment=os.getenv("ENVIRONMENT", "production"),
    )
"""
FastAPI Application for Malware Classification using Graph Neural Networks
Main entry point for the ML backend service
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
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


# Configure structured logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s %(levelname)s %(name)s: %(message)s'
)
logger = logging.getLogger("MalwareAPI")

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
        # Initialize auth DB and ensure admin user exists (with logging)
        logger.info("Calling init_db()")
        try:
            init_db()
            logger.info("init_db() completed successfully")
        except Exception:
            logger.exception("init_db() raised an exception")
            raise

        admin_user = os.environ.get('REVIEW_USER', 'admin')
        admin_pass = os.environ.get('REVIEW_PASS', 'admin')
        logger.info(f"Checking for admin user '{admin_user}'")
        try:
            user_obj = get_user(admin_user)
        except Exception:
            logger.exception("get_user() raised an exception")
            user_obj = None

        if user_obj is None:
            logger.info(f"Admin user '{admin_user}' not found; creating")
            try:
                create_user(admin_user, admin_pass)
                logger.info(f"Admin user '{admin_user}' created")
            except Exception:
                logger.exception("create_user() failed")
                raise
        else:
            logger.info(f"Admin user '{admin_user}' already exists")

        # Ensure models exist and start loading in background so startup is fast
        import asyncio

        async def _load_models_bg():
            logger.info("Background model loading task starting")
            try:
                await asyncio.to_thread(model_loader._ensure_models)
                logger.info("Background model loading completed")
            except Exception:
                logger.exception("Background model loading failed")
                raise

        # kick off background model loading and attach task to app state
        app.state.models_loading_task = asyncio.create_task(_load_models_bg())

        # Attach a done callback to log any unhandled exceptions from the task
        def _models_task_done(task):
            try:
                exc = task.exception()
                if exc is not None:
                    logger.error(f"Models loading task raised an exception: {exc}")
                else:
                    logger.info("Models loading task finished without exception")
            except asyncio.CancelledError:
                logger.warning("Models loading task was cancelled")
            except Exception as _e:
                logger.error(f"Error inspecting models task result: {_e}")

        try:
            app.state.models_loading_task.add_done_callback(_models_task_done)
        except Exception:
            logger.exception("Could not attach done callback to models task")
    except Exception as e:
        logger.exception(f"Failed during startup lifespan: {e}")
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

    @app.get("/")
    async def root():
        return {"message": "Malware Classification API is running"}
    
    # Add state for model loader
    app.state.model_loader = model_loader
    app.state.limiter = limiter
    app.state.revoked_tokens = set()
    

    # CORS Configuration
    allowed_origins = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:8080,http://localhost:3000").split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        max_age=3600,
    )

    
    # Compression middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # Fallback CORS middleware: ensure demo clients receive CORS headers
    @app.middleware("http")
    async def add_cors_headers(request: Request, call_next):
        # Handle preflight
        if request.method == "OPTIONS":
            return Response(status_code=200, headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET,POST,OPTIONS,PUT,DELETE",
                "Access-Control-Allow-Headers": "*"
            })

            def register_exception_handlers(app: FastAPI):
                # Centralized error handler for HTTPException
                @app.exception_handler(HTTPException)
                async def http_exception_handler(request: Request, exc: HTTPException):
                    logger.error(f"HTTPException: {exc.detail}")
                    return JSONResponse(
                        status_code=exc.status_code,
                        content={
                            "error": exc.__class__.__name__,
                            "message": exc.detail,
                            "timestamp": datetime.utcnow().isoformat()
                        },
                    )

                # Centralized error handler for generic exceptions
                @app.exception_handler(Exception)
                async def generic_exception_handler(request: Request, exc: Exception):
                    logger.error(f"Unhandled Exception: {exc}", exc_info=True)
                    return JSONResponse(
                        status_code=500,
                        content={
                            "error": exc.__class__.__name__,
                            "message": str(exc),
                            "timestamp": datetime.utcnow().isoformat()
                        },
                    )

        response = await call_next(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response
    

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

    # Compatibility endpoint: provide root-level /health for older integrations/tests
    @app.get('/health')
    async def compatibility_health():
        try:
            loaded = bool(model_loader.is_ready()) if hasattr(model_loader, 'is_ready') else False
        except Exception:
            loaded = False
        return JSONResponse({
            "status": "ok",
            "model_loaded": loaded,
            "model_ready": False,
            "model_path": None
        })

    @app.get('/metrics')
    async def metrics_endpoint():
        data = generate_latest()
        return Response(content=data, media_type=CONTENT_TYPE_LATEST)

    # expose analysis result cache for evaluation route
    try:
        app.state.results_cache = analysis.results_cache
    except Exception:
        app.state.results_cache = {}

    # Explicit OPTIONS handler for API prefixed routes to ensure preflight
    @app.options('/api/v1/{path:path}')
    async def api_preflight(path: str, request: Request):
        return Response(status_code=200, headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET,POST,OPTIONS,PUT,DELETE",
            "Access-Control-Allow-Headers": request.headers.get('access-control-request-headers', '*')
        })
    
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
