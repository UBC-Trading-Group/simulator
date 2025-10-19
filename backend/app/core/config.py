"""
Application configuration settings
"""

import os
from typing import List, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://user:password@postgres/trading_simulator"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Trading Simulator"

    # Trading
    MAX_ORDERS_PER_USER: int = 1000
    MAX_POSITION_SIZE: float = 1000000.0
    SESSION_DURATION_MINUTES: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
