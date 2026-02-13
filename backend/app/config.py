"""
Configuration management for the malware classification API
Supports environment-based and file-based configuration
"""

import os
from typing import List
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # API Configuration
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    api_title: str = "Malware Classification API"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Model Configuration
    model_dir: str = os.getenv("MODEL_DIR", "./models")
    gnn_model_path: str = os.getenv("GNN_MODEL_PATH", "./models/gnn_model.pt")
    baseline_model_dir: str = os.getenv("BASELINE_MODEL_DIR", "./models/baseline")
    
    # Data Configuration
    max_upload_size_mb: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50"))
    allowed_file_types: List[str] = ["csv", "json", "pcap"]
    
    # CORS Configuration
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8082",
        "http://localhost:8080",
        "http://localhost",
        os.getenv("FRONTEND_URL", "http://localhost:3000")
    ]
    
    # Rate Limiting
    rate_limit_enabled: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    rate_limit_requests: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    rate_limit_window: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # seconds
    
    # Security
    api_key_enabled: bool = os.getenv("API_KEY_ENABLED", "false").lower() == "true"
    api_key: str = os.getenv("API_KEY", "")
    
    # ML Configuration
    inference_timeout: int = int(os.getenv("INFERENCE_TIMEOUT", "60"))
    batch_size: int = int(os.getenv("BATCH_SIZE", "32"))
    
    # Result Storage (in-memory cache)
    max_cache_size: int = int(os.getenv("MAX_CACHE_SIZE", "1000"))
    cache_ttl_seconds: int = int(os.getenv("CACHE_TTL_SECONDS", "3600"))
    
    # Feature Extraction
    graph_max_nodes: int = int(os.getenv("GRAPH_MAX_NODES", "1000"))
    graph_timeout: int = int(os.getenv("GRAPH_TIMEOUT", "30"))
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
