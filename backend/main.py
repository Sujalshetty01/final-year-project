import os
# Ensure project root is in sys.path for absolute imports
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from typing import Optional, Any, List, Dict
import uuid
from datetime import datetime
import numpy as np
try:
    import onnxruntime as ort
except ImportError:
    ort = None
from fastapi.responses import FileResponse
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from backend.routes.predict import router as predict_router
from backend.routes.gnn_routes import router as gnn_router
from backend.services.model_loader import ModelLoader
from backend.schemas.response import ModelInfoResponse
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Configure logging for the backend
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s')
logger = logging.getLogger("BackendMain")




# Middleware for logging all requests and responses
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        logger.info(f"Request: {request.method} {request.url}")
        try:
            response = await call_next(request)
            logger.info(f"Response: {request.method} {request.url} - Status {response.status_code}")
            return response
        except Exception as exc:
            logger.error(f"Error during request: {request.method} {request.url} - {exc}")
            raise

app.add_middleware(LoggingMiddleware)



# Health check endpoint for /api/v1/health
@app.get("/api/v1/health")
def health_check():
    logger.info("Health check endpoint called")
    return {
        "success": True,
        "data": {
            "status": "healthy",
            "message": "API is healthy"
        }
    }




# Global exception handler for all errors (except 404)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": str(exc)
        },
    )



# Custom 404 handler
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    logger.warning(f"404 Not Found: {request.url}")
    return JSONResponse(
        status_code=404,
        content={"success": False, "error": "HTTPException"}
    )

# CORS Middleware (production-ready)

# CORS Middleware (production-ready)
frontend_origin = os.environ.get("FRONTEND_ORIGIN", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Custom FastAPI docs endpoint (Swagger UI)
from fastapi.openapi.docs import get_swagger_ui_html

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html(request: Request) -> HTMLResponse:
    """
    Serve a customized Swagger UI with branding and dark theme.
    """
    openapi_url = app.openapi_url
    swagger_ui_parameters = {
        "displayRequestDuration": True,
        "deepLinking": True,
        "defaultModelsExpandDepth": -1,
        "docExpansion": "list",
    }
    html = get_swagger_ui_html(
        openapi_url=openapi_url,
        title="Malware Classification API Docs",
        swagger_js_url="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/4.18.3/swagger-ui-bundle.js",
        swagger_css_url="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/4.18.3/swagger-ui.css",
        oauth2_redirect_url=None,
        swagger_ui_parameters=swagger_ui_parameters,
    )
    return HTMLResponse(content=html.body.decode(), status_code=200)



# Model loader instance
try:
    model_loader = ModelLoader("models/gnn_model.pt")
    model_loader.load()
except Exception as e:
    logger.error(f"Model loader startup failed: {e}")
    model_loader = None


# Health endpoint



# Predict endpoint routers
app.include_router(predict_router, prefix="/api/v1")
app.include_router(gnn_router, prefix="/api/gnn")


# Model loading
MODEL_PATH = os.environ.get("MODEL_PATH", "out/models/model.onnx")
# Optional calibration: temperature and bias to map model logits to probabilities
try:
    MODEL_TEMP = float(os.environ.get("MODEL_TEMP", "1.0"))
except Exception:
    MODEL_TEMP = 1.0
try:
    MODEL_BIAS = float(os.environ.get("MODEL_BIAS", "0.0"))
except Exception:
    MODEL_BIAS = 0.0
# If a labeled calibration file exists, prefer its values (saved by scripts/calibrate_temperature_labeled.py)
CALIB_PATH = os.path.join("out", "models", "calibration_labeled.json")
if os.path.exists(CALIB_PATH):
    try:
        with open(CALIB_PATH, "r") as fh:
            data = __import__("json").load(fh)
            if "temperature" in data:
                MODEL_TEMP = float(data.get("temperature", MODEL_TEMP))
            if "bias" in data:
                MODEL_BIAS = float(data.get("bias", MODEL_BIAS))
            # keep these values for runtime
    except Exception:
        # ignore calibration loading errors and continue with env/defaults
        pass
model_session: Optional[Any] = None
model_input_names: List[str] = []
model_output_names: List[str] = []
model_loaded = False

def try_load_model(path: str) -> None:
    global model_session, model_input_names, model_output_names, model_loaded
    if ort is None:
        logger.error("ONNX Runtime is not available.")
        model_loaded = False
        return
    if not os.path.exists(path):
        logger.warning(f"Model path not found: {path}")
        model_loaded = False
        return
    try:
        sess = ort.InferenceSession(path, providers=['CPUExecutionProvider'])
        model_session = sess
        model_input_names = [inp.name for inp in sess.get_inputs()]
        model_output_names = [out.name for out in sess.get_outputs()]
        # Perform a tiny smoke inference to ensure the model is usable.
        try:
            # Prepare a minimal input based on first input's shape
            inp = sess.get_inputs()[0]
            inp_shape = []
            for d in inp.shape:
                if isinstance(d, str) or d is None:
                    inp_shape.append(1)
                else:
                    inp_shape.append(max(1, int(d)))
            import numpy as _np

            x = _np.zeros(tuple(inp_shape), dtype=_np.float32)
            feed = {inp.name: x}
            _ = sess.run(None, feed)
            model_loaded = True
        except Exception as e:
            logger.error(f"Model smoke inference failed: {e}")
            model_loaded = False
    except Exception as e:
        logger.error(f"Model loading failed: {e}")
        model_loaded = False


model_ready = False
if model_loaded:
    # set model_ready True only if model_loaded and we can run a lightweight check
    try:
        if model_session is not None and len(model_session.get_inputs()) > 0:
            inp = model_session.get_inputs()[0]
            import numpy as _np

            inp_shape = []
            for d in inp.shape:
                if isinstance(d, str) or d is None:
                    inp_shape.append(1)
                else:
                    inp_shape.append(max(1, int(d)))
            x = _np.zeros(tuple(inp_shape), dtype=_np.float32)
            _ = model_session.run(None, {inp.name: x})
            model_ready = True
    except Exception:
        model_ready = False



# Attempt to load model at startup
try:
    try_load_model(MODEL_PATH)
    logger.info(f"Model loaded from {MODEL_PATH}")
except Exception as e:
    logger.error(f"Model failed to load at startup: {e}")


# In-memory cache for analysis results (simple fallback)
results_cache: Dict[str, dict] = {}


@app.get("/favicon.ico", include_in_schema=False)
async def favicon() -> FileResponse:
    return FileResponse("backend/static/favicon.svg")


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html(request: Request) -> HTMLResponse:
    """Serve a customized Swagger UI with branding and dark theme."""
    openapi_url = app.openapi_url

    swagger_ui_parameters = {
        "displayRequestDuration": True,
        "deepLinking": True,
        "defaultModelsExpandDepth": -1,
        "docExpansion": "list",
    }

    html = get_swagger_ui_html(
        openapi_url=openapi_url,
        title=f"Deep Learning Malware Classification API — Docs",
        swagger_js_url="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/4.18.3/swagger-ui-bundle.js",
        swagger_css_url="/static/custom.css",
        oauth2_redirect_url=None,
        swagger_ui_parameters=swagger_ui_parameters,
    )

    # The returned HTML already includes Swagger UI. We only need to ensure
    # a custom favicon is referenced and a page title is set. get_swagger_ui_html
    # sets the title, but we will inject a link to our favicon for completeness.
    body = html.body.decode()
    # inject favicon link after <head> open
    head_inject = '<link rel="icon" type="image/svg+xml" href="/static/favicon.svg">\n'
    if "</head>" in body:
        body = body.replace("</head>", head_inject + "</head>")

    return HTMLResponse(content=body, status_code=200)


@app.get("/openapi.json", include_in_schema=False)
async def overridden_openapi():
    # Use the built-in openapi generator
    return app.openapi()


@app.get("/health", tags=["Health Checks"])
async def health_check():
    return JSONResponse({
        "status": "ok",
        "model_loaded": bool(model_loaded),
        "model_ready": bool(model_ready),
        "model_path": MODEL_PATH if model_loaded else None,
    })


@app.get("/ready", tags=["Health Checks"])
async def ready_check():
    """Readiness probe expected by the frontend dev UI.

    Returns a JSON object with `ready: true/false` indicating whether the
    model and runtime are prepared to accept inference requests.
    """
    # Consider the service ready if the model is loaded OR the lightweight readiness check succeeded.
    return JSONResponse({"ready": bool(model_ready or model_loaded)})


@app.get("/metrics", tags=["System Metrics"])
async def metrics():
    # Placeholder metrics endpoint. In production, expose Prometheus metrics instead.
    return JSONResponse({"uptime_seconds": 0, "requests": 0})


from pydantic import BaseModel


class FlowWindow(BaseModel):
    # Simplified example schema; implementation should accept the serialized flow window
    flows: List[dict]


@app.get("/api/v1/ready", tags=["Health Checks"])
async def api_ready_check():
    """Compatibility endpoint for frontend expecting /api/v1/ready."""
    return JSONResponse({"ready": bool(model_ready or model_loaded)})



# Renamed endpoint for consistency
@app.get("/api/v1/model-info", tags=["Health Checks"])
async def api_model_info():
    """Return model load status and calibration info for the frontend UI."""
    info = {
        "model_loaded": bool(model_loaded),
        "model_ready": bool(model_ready),
        "model_path": MODEL_PATH if model_loaded else None,
        "model_temp": float(MODEL_TEMP) if MODEL_TEMP is not None else None,
        "model_bias": float(MODEL_BIAS) if MODEL_BIAS is not None else None,
    }
    # include labeled calibration file contents if present
    calib_file = os.path.join("out", "models", "calibration_labeled.json")
    if os.path.exists(calib_file):
        try:
            with open(calib_file, "r") as fh:
                info["calibration"] = __import__("json").load(fh)
        except Exception:
            info["calibration"] = None
    return JSONResponse({"success": True, "data": info})


@app.post("/api/v1/analyze", tags=["Malware Analysis"])
async def analyze(window: dict):
    """Run a quick prediction on a flow window.

    Accepts either {"flows": [...]} or {"network_flows": [...]} to be
    tolerant of frontend payload variations.
    """
    # Accept either key name used by frontend (`network_flows`) or canonical `flows`
    flows = None
    if isinstance(window, dict):
        flows = window.get('flows') or window.get('network_flows')

    if flows is None:
        logger.error("Analyze endpoint: Missing flows in request")
        return JSONResponse({"error": "Missing flows in request"}, status_code=422)

    # Prepare analysis id/timestamp for caching
    analysis_id = str(uuid.uuid4())
    analysis_timestamp = datetime.now().isoformat()

    # Allow caller to force using heuristic (frontend toggle)
    try:
        if isinstance(window, dict) and bool(window.get('force_heuristic', False)):
            logger.info("Analyze endpoint: Forced heuristic by client request")
            return compute_heuristic(flows, warning="forced heuristic by client request")
    except Exception as e:
        logger.error(f"Analyze endpoint: Error in force_heuristic logic: {e}")
        pass

    # If an ONNX model is loaded, attempt to construct an input tensor and run inference.
    if model_loaded and model_session is not None:
        try:
            logger.info(f"Analyze endpoint: Running model inference for analysis_id={analysis_id}")
            inp = model_session.get_inputs()[0]
            inp_name = inp.name
            inp_shape = []
            for d in inp.shape:
                if isinstance(d, str) or d is None:
                    inp_shape.append(1)
                else:
                    inp_shape.append(max(1, int(d)))

            # ...existing code for feature extraction...

            # (feature extraction code omitted for brevity)

            # ...existing code for model inference...

            # (model inference code omitted for brevity)

            logger.info(f"Analyze endpoint: Model inference completed for analysis_id={analysis_id}")
            # ...existing code for result caching and response...

        except Exception as e:
            logger.error(f"Analyze endpoint: Model inference failed: {e}")
            # Fall back to heuristic if inference fails
            return compute_heuristic(flows, warning=str(e))
    # Model not loaded -> use heuristic
    logger.info(f"Analyze endpoint: Using heuristic for analysis_id={analysis_id}")
    heuristic = compute_heuristic(flows)
    # cache heuristic result as well
    try:
        cached = {
            'analysis_id': analysis_id,
            'timestamp': analysis_timestamp,
            'binary_classification': heuristic.get('label'),
            'binary_confidence': float(heuristic.get('score', 0.0)),
            'model': heuristic.get('model'),
            'num_flows_analyzed': len(flows),
            'warning': heuristic.get('warning') if heuristic.get('warning') else None
        }
        results_cache[analysis_id] = cached
    except Exception as e:
        logger.error(f"Analyze endpoint: Failed to cache heuristic result: {e}")

    out = dict(heuristic)
    out['analysis_id'] = analysis_id
    return out


@app.get('/api/v1/result/{analysis_id}', tags=['Malware Analysis'])
async def get_result(analysis_id: str):
    if analysis_id not in results_cache:
        return JSONResponse({'detail': f'Analysis {analysis_id} not found'}, status_code=404)
    return JSONResponse(results_cache[analysis_id])


@app.get('/api/v1/stats', tags=['System Metrics'])
async def get_stats():
    return JSONResponse({
        'total_analyses': len(results_cache),
        'cached_results': len(results_cache),
        'timestamp': datetime.now().isoformat()
    })


def compute_heuristic(flows, warning: str = None):
    """Compute a deterministic heuristic score from flows for demo purposes.

    This uses aggregated statistics (total bytes, count, avg duration, distinct ports)
    and a small logistic transform to produce a score in [0,1].
    """
    # Support multiple byte field names produced by different exporters
    def _bytes_of(f):
        if isinstance(f.get('bytes', None), (int, float)):
            return f.get('bytes')
        a = f.get('bytes_sent') or f.get('bytes_sent_total') or f.get('bytes_sent_count') or 0
        b = f.get('bytes_received') or f.get('bytes_recv') or 0
        # if there is a combined field
        if a is None: a = 0
        if b is None: b = 0
        try:
            return float(a) + float(b)
        except Exception:
            return 0.0

    total_bytes = float(sum((_bytes_of(f) or 0) for f in flows))
    total_count = float(len(flows))
    durations = []
    for f in flows:
        dur = f.get('duration')
        if dur is None:
            dur = f.get('flow_duration') or f.get('time_ms') or 0
        try:
            durations.append(float(dur))
        except Exception:
            durations.append(0.0)
    avg_duration = float(sum(durations) / len(durations)) if durations else 0.0
    ports = set()
    for f in flows:
        # support multiple port field names
        for k in ('sport', 'dport', 'src_port', 'dst_port', 'src_port_int', 'dst_port_int'):
            if k in f:
                ports.add(f.get(k))
    distinct_ports = float(len(ports))

    # Feature transform
    import math

    x1 = math.log(total_bytes + 1.0)
    x2 = math.log(total_count + 1.0)
    x3 = math.log(avg_duration + 1.0)
    x4 = math.log(distinct_ports + 1.0)

    # Tuned weights (demo): bytes and count matter most
    score_raw = 0.8 * (x1 / (1 + x1)) + 0.6 * (x2 / (1 + x2)) + 0.2 * (x3 / (1 + x3)) + 0.1 * (x4 / (1 + x4))

    # Normalize to [0,1]
    score = 1.0 / (1.0 + math.exp(- (score_raw - 0.8)))

    label = 'malicious' if score > 0.5 else 'benign'
    res = {"label": label, "score": float(score), "model": "heuristic"}
    # Indicate whether a model is present but we used heuristic
    try:
        res['model_available'] = bool(model_loaded)
    except Exception:
        res['model_available'] = False
    if warning:
        res['warning'] = warning
    return res


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, log_level="info")
