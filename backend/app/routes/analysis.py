"""
Analysis endpoints for malware classification
Includes POST /analyze and GET /result/{id} endpoints
"""

from fastapi import APIRouter, Request, HTTPException, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from datetime import datetime
import time
import uuid
import logging
from typing import Dict, Any

from app.models.schemas import (
    AnalysisRequest, AnalysisResponse, PredictionResult,
    GraphFeatures, ErrorResponse
)

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory result storage (in production, use database)
results_cache: Dict[str, AnalysisResponse] = {}


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_malware(request: Request) -> AnalysisResponse:
    """
    Analyze network flows for malware classification
    
    POST /api/v1/analyze
    
    Args:
        analysis: AnalysisRequest with network flows
        
    Returns:
        AnalysisResponse with predictions and confidence scores
    """
    try:
        # Get model loader
        model_loader = request.app.state.model_loader
        if model_loader is None or not model_loader.models_loaded:
            raise HTTPException(
                status_code=503,
                detail="Models not loaded. Service not ready for inference."
            )
        
        # Start timer
        start_time = time.time()
        analysis_start = time.time()
        # Parse request body: support JSON body or multipart upload with a 'file' field
        analysis = None
        content_type = request.headers.get('content-type', '')
        if content_type.startswith('multipart/'):
            form = await request.form()
            # If frontend sends a file field, attempt to read and parse it as JSON
            if 'file' in form:
                file_field = form['file']
                try:
                    # UploadFile-like objects support .read()
                    if hasattr(file_field, 'read'):
                        raw = await file_field.read()
                    else:
                        raw = str(file_field)
                    import json as _json
                    if isinstance(raw, (bytes, bytearray)):
                        raw = raw.decode('utf-8')
                    parsed = _json.loads(raw)
                    # If the uploaded JSON is a raw list of flows, wrap it
                    if isinstance(parsed, list):
                        parsed = {"network_flows": parsed}
                except Exception as e:
                    raise HTTPException(status_code=400, detail=f"Invalid JSON in uploaded file: {e}")
                # Build AnalysisRequest from parsed payload
                analysis = AnalysisRequest.parse_obj(parsed)
        else:
            # Assume JSON body
            try:
                body = await request.json()
            except Exception:
                raise HTTPException(status_code=400, detail="Invalid JSON body")
            analysis = AnalysisRequest.parse_obj(body)

        # Validate input
        if not analysis.network_flows or len(analysis.network_flows) == 0:
            raise HTTPException(
                status_code=400,
                detail="network_flows cannot be empty"
            )

        if len(analysis.network_flows) > 10000:
            raise HTTPException(
                status_code=400,
                detail="network_flows exceeds maximum size (10000)"
            )
        
        # Generate analysis ID
        analysis_id = str(uuid.uuid4())
        logger.info(f"Starting analysis {analysis_id} with {len(analysis.network_flows)} flows")
        
        # Get predictions from models
        feature_extraction_start = time.time()
        predictions = await model_loader.predict(
            flows=analysis.network_flows,
            use_gnn=True,
            use_baseline=analysis.use_ensemble,
            use_cache=True
        )
        feature_extraction_time = (time.time() - feature_extraction_start) * 1000
        
        # Extract graph features
        graph_features = predictions.get('graph_features', {})
        graph_features_obj = GraphFeatures(
            num_nodes=graph_features.get('num_nodes', 0),
            num_edges=graph_features.get('num_edges', 0),
            avg_degree=graph_features.get('avg_degree', 0.0),
            density=graph_features.get('density', 0.0),
            average_shortest_path=graph_features.get('graph_diameter'),
            clustering_coefficient=graph_features.get('average_clustering')
        ) if analysis.enable_detailed_analysis else None
        
        # GNN prediction
        gnn_pred_data = predictions.get('gnn_prediction')
        gnn_prediction = None
        if gnn_pred_data:
            gnn_prediction = PredictionResult(
                model_name=gnn_pred_data['model_name'],
                predicted_label=gnn_pred_data['predicted_label'],
                confidence=gnn_pred_data['confidence'],
                probabilities=gnn_pred_data['probabilities']
            )
        
        # Baseline predictions
        baseline_predictions = None
        if analysis.use_ensemble:
            baseline_preds = predictions.get('baseline_predictions', {})
            baseline_predictions = []
            for model_name, pred_data in baseline_preds.items():
                baseline_predictions.append(
                    PredictionResult(
                        model_name=pred_data.get('model_name', model_name),
                        predicted_label=pred_data['predicted_label'],
                        confidence=pred_data['confidence'],
                        probabilities=pred_data['probabilities']
                    )
                )
        
        # Determine primary classification
        binary_classification = "benign"
        binary_confidence = 0.5
        family_classification = None
        family_confidence = None
        
        if gnn_prediction:
            binary_classification = gnn_prediction.predicted_label
            binary_confidence = gnn_prediction.confidence
            
            # Determine malware family
            if binary_classification == "malware":
                family_classification = "unknown"  # Could be enhanced with family classifier
                family_confidence = binary_confidence
        
        # Calculate overall risk score
        confidence_scores = [binary_confidence]
        if baseline_predictions:
            confidence_scores.extend([p.confidence for p in baseline_predictions])
        
        # Risk score: average of confidence for malware prediction
        if binary_classification == "malware":
            risk_score = sum(confidence_scores) / len(confidence_scores)
        else:
            risk_score = 1.0 - (sum(confidence_scores) / len(confidence_scores))
        
        inference_time = (time.time() - start_time) * 1000
        total_time = (time.time() - analysis_start) * 1000
        
        # Create response
        response = AnalysisResponse(
            analysis_id=analysis_id,
            timestamp=datetime.now(),
            app_name=analysis.app_name,
            binary_classification=binary_classification,
            binary_confidence=binary_confidence,
            family_classification=family_classification,
            family_confidence=family_confidence,
            gnn_prediction=gnn_prediction,
            baseline_predictions=baseline_predictions if analysis.use_ensemble else None,
            graph_features=graph_features_obj,
            num_flows_analyzed=len(analysis.network_flows),
            feature_extraction_time_ms=feature_extraction_time,
            inference_time_ms=inference_time,
            total_time_ms=total_time,
            risk_score=risk_score
        )
        
        # Prepare JSON-serializable response and add legacy compatibility fields
        resp_dict = jsonable_encoder(response)
        # Legacy fields expected by older clients/tests
        resp_dict.setdefault('label', binary_classification)
        resp_dict.setdefault('score', binary_confidence)

        # Cache result (store the Pydantic model for internal use)
        results_cache[analysis_id] = response

        logger.info(f"Analysis {analysis_id} completed in {total_time:.2f}ms. "
                   f"Result: {binary_classification} ({binary_confidence:.2%})")

        # Return JSON response (already encoded)
        return JSONResponse(content=resp_dict)
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in analyze endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/result/{analysis_id}", response_model=AnalysisResponse)
async def get_result(request: Request, analysis_id: str) -> AnalysisResponse:
    """
    Retrieve a cached analysis result
    
    GET /api/v1/result/{analysis_id}
    
    Args:
        analysis_id: ID of the analysis to retrieve
        
    Returns:
        Cached AnalysisResponse
    """
    try:
        if analysis_id not in results_cache:
            raise HTTPException(
                status_code=404,
                detail=f"Analysis {analysis_id} not found"
            )
        
        result = results_cache[analysis_id]
        logger.info(f"Retrieved cached result for {analysis_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving result: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving result: {str(e)}"
        )


@router.get("/stats")
async def get_stats(request: Request) -> Dict[str, Any]:
    """
    Get API statistics
    
    GET /api/v1/stats
    """
    model_loader = request.app.state.model_loader
    
    return {
        'total_analyses': len(results_cache),
        'cached_results': len(results_cache),
        'model_status': model_loader.get_status() if model_loader else None,
        'timestamp': datetime.now().isoformat()
    }
