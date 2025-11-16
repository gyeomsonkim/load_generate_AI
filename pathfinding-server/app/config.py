"""
Application configuration settings
"""
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Application
    app_name: str = Field(default="Pathfinding Server")
    app_version: str = Field(default="1.0.0")
    debug: bool = Field(default=False)
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)

    # Database
    database_url: str = Field(default="postgresql+asyncpg://localhost/pathfinding_db")
    database_echo: bool = Field(default=False)

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0")
    redis_ttl: int = Field(default=3600)

    # Storage
    storage_type: str = Field(default="local")  # local or minio
    storage_path: str = Field(default="./storage")
    minio_endpoint: str = Field(default="localhost:9000")
    minio_access_key: str = Field(default="minioadmin")
    minio_secret_key: str = Field(default="minioadmin")
    minio_bucket: str = Field(default="pathfinding-maps")
    minio_secure: bool = Field(default=False)

    # ML Settings
    ml_model_path: str = Field(default="./ml_models")
    ml_device: str = Field(default="cpu")
    ml_batch_size: int = Field(default=4)

    # Pathfinding
    max_path_distance: int = Field(default=10000)
    default_walkway_width: int = Field(default=10)
    path_smoothing: bool = Field(default=True)
    cache_paths: bool = Field(default=True)

    # API
    api_prefix: str = Field(default="/api/v1")
    cors_origins: List[str] = Field(default=["*"])
    max_upload_size: int = Field(default=52428800)  # 50MB

    # Security
    secret_key: str = Field(default="change-this-secret-key-in-production")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()