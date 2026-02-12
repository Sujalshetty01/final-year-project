from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from typing import List

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
    return JSONResponse({"status": "ok"})


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
    # Dummy heuristic: if any flow has bytes > 1e6 mark as suspicious
    suspicious = any((f.get("bytes", 0) or 0) > 1_000_000 for f in window.flows)
    score = 0.9 if suspicious else 0.1
    label = "malicious" if suspicious else "benign"
    return {"label": label, "score": score}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, log_level="info")
