from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from typing import List, Optional, Any
import os
import numpy as np
try:
    import onnx
    import onnxruntime as ort
except Exception:
    onnx = None
    ort = None

tags_metadata = [
    {
        "name": "Malware Analysis",
        "description": "Endpoints for submitting flow windows and receiving GNN-based malware classification results.",
    },
    {
        "name": "Health Checks",
        "description": "Liveness and readiness probes for the service.",
    },
    {
        "name": "System Metrics",
        "description": "Operational metrics and diagnostics endpoints (Prometheus-compatible).",
    },
]

app = FastAPI(
    title="Deep Learning Malware Classification API",
    description=(
        "API for a Graph Neural Network (GNN) based malware classification system. "
        "Submit serialized network flow windows (or simplified JSON examples) to receive "
        "binary malware/benign predictions. The backend loads ONNX-exported models and "
        "serves inference via `onnxruntime` for low-latency CPU inference."
    ),
    version="1.0.0",
    contact={"name": "Sujal Shetty", "email": "your-email@example.com"},
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
    docs_url=None,
    redoc_url=None,
    openapi_tags=tags_metadata,
)

# Mount static assets for logo, favicon and custom CSS
app.mount("/static", StaticFiles(directory="backend/static"), name="static")

# Model loading
MODEL_PATH = os.environ.get("MODEL_PATH", "out/models/model.onnx")
model_session: Optional[Any] = None
model_input_names: List[str] = []
model_output_names: List[str] = []
model_loaded = False

def try_load_model(path: str):
    global model_session, model_input_names, model_output_names, model_loaded
    if ort is None:
        model_loaded = False
        return
    if not os.path.exists(path):
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
        except Exception:
            model_loaded = False
    except Exception:
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
try_load_model(MODEL_PATH)


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


@app.get("/metrics", tags=["System Metrics"])
async def metrics():
    # Placeholder metrics endpoint. In production, expose Prometheus metrics instead.
    return JSONResponse({"uptime_seconds": 0, "requests": 0})


from pydantic import BaseModel


class FlowWindow(BaseModel):
    # Simplified example schema; implementation should accept the serialized flow window
    flows: List[dict]


@app.post("/api/v1/analyze", tags=["Malware Analysis"])
async def analyze(window: FlowWindow):
    """Run a quick prediction on a flow window (dummy implementation).

    Replace the body of this handler with ONNX runtime inference that loads
    a model from disk (e.g., `out/models/model.onnx`) and returns prediction.
    """
    # If an ONNX model is loaded, attempt to construct an input tensor and run inference.
    if model_loaded and model_session is not None:
        try:
            # Best-effort: use first model input and construct a numpy array with shape
            # replacing dynamic dims with 1. Many exported models include a single float input.
            inp = model_session.get_inputs()[0]
            inp_name = inp.name
            inp_shape = []
            for d in inp.shape:
                if isinstance(d, str) or d is None:
                    inp_shape.append(1)
                else:
                    inp_shape.append(max(1, int(d)))
            # Create a dummy feature vector by summarizing flows: total bytes and count
            total_bytes = float(sum((f.get("bytes", 0) or 0) for f in window.flows))
            total_count = float(len(window.flows))
            # Prepare an input array matching input size (use zeros and place our simple features)
            x = np.zeros(tuple(inp_shape), dtype=np.float32)
            # Fill leading elements if possible
            flat = x.ravel()
            if flat.size >= 2:
                flat[0] = total_bytes
                flat[1] = total_count
            else:
                flat[0] = total_bytes
            feed = {inp_name: x}
            outputs = model_session.run(None, feed)
            # Return first output as score
            out0 = outputs[0]
            # If output is array-like, summarize
            if hasattr(out0, 'tolist'):
                out_val = float(np.asarray(out0).ravel()[0])
            else:
                out_val = float(out0)
            label = "malicious" if out_val > 0.5 else "benign"
            return {"label": label, "score": out_val, "model": os.path.basename(MODEL_PATH)}
        except Exception as e:
            # Fall back to heuristic on inference error
            suspicious = any((f.get("bytes", 0) or 0) > 1_000_000 for f in window.flows)
            score = 0.9 if suspicious else 0.1
            label = "malicious" if suspicious else "benign"
            return {"label": label, "score": score, "warning": str(e)}

    # Fallback: simple heuristic if model not loaded
    suspicious = any((f.get("bytes", 0) or 0) > 1_000_000 for f in window.flows)
    score = 0.9 if suspicious else 0.1
    label = "malicious" if suspicious else "benign"
    return {"label": label, "score": score}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, log_level="info")
