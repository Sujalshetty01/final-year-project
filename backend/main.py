

import os
from typing import Optional, Any, List, Dict
import onnxruntime as ort
from fastapi.responses import FileResponse
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from backend.routes.predict import router as predict_router
from backend.routes.gnn_routes import router as gnn_router
from backend.services.model_loader import ModelLoader
from backend.schemas.response import ModelInfoResponse
import logging

# Configure logging for the backend
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s')
logger = logging.getLogger("BackendMain")


app = FastAPI(title="Malware Classification API")

# CORS Middleware (production-ready)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific domains in production
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
model_loader = ModelLoader("models/gnn_model.pt")
model_loader.load()


# Health endpoint
@app.get("/health")
def health() -> JSONResponse:
    """Basic health check endpoint."""
    return JSONResponse({"status": "ok"})


# Model info endpoint
@app.get("/api/v1/model-info", response_model=ModelInfoResponse)
def model_info() -> ModelInfoResponse:
    """Return model metadata and status."""
    info = model_loader.get_info()
    # Example: add accuracy and classes if available
    return ModelInfoResponse(
        name=info.get("name", "GNNModel"),
        accuracy=0.95,  # Replace with actual value
        classes=["benign", "malware"],
        device=info.get("device", "cpu"),
        loaded=info.get("loaded", False)
    )


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


@app.get("/api/v1/model_info", tags=["Health Checks"])
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
    return JSONResponse(info)


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
        return JSONResponse({"error": "Missing flows in request"}, status_code=422)

    # Prepare analysis id/timestamp for caching
    analysis_id = str(uuid.uuid4())
    analysis_timestamp = datetime.now().isoformat()

    # Allow caller to force using heuristic (frontend toggle)
    try:
        if isinstance(window, dict) and bool(window.get('force_heuristic', False)):
            return compute_heuristic(flows, warning="forced heuristic by client request")
    except Exception:
        pass

    # If an ONNX model is loaded, attempt to construct an input tensor and run inference.
    if model_loaded and model_session is not None:
        try:
            inp = model_session.get_inputs()[0]
            inp_name = inp.name
            inp_shape = []
            for d in inp.shape:
                if isinstance(d, str) or d is None:
                    inp_shape.append(1)
                else:
                    inp_shape.append(max(1, int(d)))

            # Create a normalized feature vector from flows so the model receives
            # inputs similar in scale to training data. We compute log-scaled
            # totals and simple aggregates (mean bytes, avg duration, distinct ports).
            def _bytes_of(f):
                if isinstance(f.get('bytes', None), (int, float)):
                    return float(f.get('bytes', 0))
                a = f.get('bytes_sent') or f.get('bytes_sent_total') or 0
                b = f.get('bytes_received') or f.get('bytes_recv') or 0
                try:
                    return float(a) + float(b)
                except Exception:
                    return 0.0

            total_bytes = float(sum((_bytes_of(f) or 0.0) for f in flows))
            total_count = float(len(flows))

            # durations and basic stats
            durations = []
            byte_vals = []
            ports = []
            for f in flows:
                dur = f.get('duration')
                if dur is None:
                    dur = f.get('flow_duration') or f.get('time_ms') or 0
                try:
                    durations.append(float(dur))
                except Exception:
                    durations.append(0.0)

                # record per-flow bytes where possible
                try:
                    b = float(f.get('bytes', None) if f.get('bytes', None) is not None else (
                        (f.get('bytes_sent') or 0) + (f.get('bytes_received') or 0)
                    ))
                except Exception:
                    b = 0.0
                byte_vals.append(b)

                for k in ('sport', 'dport', 'src_port', 'dst_port', 'src_port_int', 'dst_port_int'):
                    if k in f and f.get(k) is not None:
                        ports.append(f.get(k))

            avg_duration = float(sum(durations) / len(durations)) if durations else 0.0
            distinct_ports = float(len(set(ports)))

            # feature transforms (log-scale where appropriate)
            import math

            f_total_bytes = math.log(total_bytes + 1.0)
            f_total_count = math.log(total_count + 1.0)
            f_avg_dur = math.log(avg_duration + 1.0)
            f_dist_ports = math.log(distinct_ports + 1.0)
            mean_bytes = total_bytes / (total_count + 1e-6)
            f_mean_bytes = math.log(mean_bytes + 1.0)

            # additional aggregated features: max/min/std bytes, port-entropy
            max_b = float(max(byte_vals)) if byte_vals else 0.0
            min_b = float(min(byte_vals)) if byte_vals else 0.0
            std_b = float(np.std(np.array(byte_vals, dtype=np.float32))) if byte_vals else 0.0
            f_max_b = math.log(max_b + 1.0)
            f_min_b = math.log(min_b + 1.0)
            f_std_b = math.log(std_b + 1.0)

            # simple port entropy estimate
            port_entropy = 0.0
            if ports:
                vals, counts = np.unique(np.array(ports), return_counts=True)
                probs = counts / counts.sum()
                # entropy in nats
                port_entropy = float(-np.sum(probs * np.log(probs + 1e-12)))
            f_port_entropy = math.log(port_entropy + 1.0)

            feats = [f_total_bytes, f_total_count, f_avg_dur, f_dist_ports, f_mean_bytes,
                     f_max_b, f_min_b, f_std_b, f_port_entropy]

            x = np.zeros(tuple(inp_shape), dtype=np.float32)
            flat = x.ravel()
            # Fill available slots with our features (truncate or zero-pad)
            for i, v in enumerate(feats):
                if i < flat.size:
                    flat[i] = float(v)
            feed = {inp_name: x}
            outputs = model_session.run(None, feed)
            out0 = outputs[0]
            arr = np.asarray(out0).ravel()

            # Post-process model outputs into probabilities
            def _sigmoid(x):
                return 1.0 / (1.0 + np.exp(-x))

            def _softmax(x):
                e = np.exp(x - np.max(x))
                return e / e.sum()

            score = 0.0
            label = "benign"
            try:
                if arr.size == 1:
                    # Single logit -> apply bias/temperature then sigmoid
                    logit = float(arr[0])
                    temp = float(MODEL_TEMP) if MODEL_TEMP and float(MODEL_TEMP) > 0.0 else 1.0
                    bias = float(MODEL_BIAS) if MODEL_BIAS else 0.0
                    adj = (logit + bias) / temp
                    prob = float(_sigmoid(adj))
                    score = prob
                    label = "malicious" if prob > 0.5 else "benign"
                elif arr.size == 2:
                    # Binary logits -> apply temperature then softmax
                    # NOTE: model's class ordering places the malicious logit at index 0
                    # based on calibration/inspection, so probability of malicious is probs[0].
                    temp = float(MODEL_TEMP) if MODEL_TEMP and float(MODEL_TEMP) > 0.0 else 1.0
                    arr_adj = arr.astype(np.float32) / temp
                    probs = _softmax(arr_adj)
                    prob_mal = float(probs[0])
                    score = prob_mal
                    label = "malicious" if prob_mal > 0.5 else "benign"
                else:
                    # Multi-class: apply temperature then softmax; choose max-prob class
                    temp = float(MODEL_TEMP) if MODEL_TEMP and float(MODEL_TEMP) > 0.0 else 1.0
                    probs = _softmax(arr.astype(np.float32) / temp)
                    idx = int(np.argmax(probs))
                    score = float(probs[idx])
                    label = "malicious" if idx == 1 else f"class_{idx}"
            except Exception:
                # Fallback: try to coerce first element
                try:
                    score = float(arr.ravel()[0])
                    label = "malicious" if score > 0.5 else "benign"
                except Exception:
                    return compute_heuristic(flows, warning="model post-processing failed")

            # Clamp score to [0,1]
            score = float(max(0.0, min(1.0, score)))
            # If model produces an extremely small/uninformative score, fall back to heuristic
            if score < 1e-4:
                warn = f"model uninformative (raw_score={score}); falling back to heuristic"
                result = compute_heuristic(flows, warning=warn)
            else:
                result = {"label": label, "score": score, "model": os.path.basename(MODEL_PATH)}

            # Cache a richer response for later retrieval
            try:
                cached = {
                    'analysis_id': analysis_id,
                    'timestamp': analysis_timestamp,
                    'binary_classification': result.get('label'),
                    'binary_confidence': float(result.get('score', 0.0)),
                    'model': result.get('model'),
                    'num_flows_analyzed': len(flows),
                    'warning': result.get('warning') if result.get('warning') else None
                }
                results_cache[analysis_id] = cached
            except Exception:
                pass

            # Return compact result plus analysis_id for client convenience
            out = dict(result)
            out['analysis_id'] = analysis_id
            return out
        except Exception as e:
            # Fall back to heuristic if inference fails
            return compute_heuristic(flows, warning=str(e))
    # Model not loaded -> use heuristic
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
    except Exception:
        pass

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
