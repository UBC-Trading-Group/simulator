"""
Application configuration settings
"""

import json
import os
from typing import List, Optional, Union

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/trading_simulator"
    DB_HOST: Optional[str] = None
    DB_PORT: Optional[str] = None
    DB_NAME: Optional[str] = None
    DB_USERNAME: Optional[str] = None
    DB_PASSWORD: Optional[str] = None

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[List[str], str]) -> List[str]:
        if isinstance(v, str):
            # Try to parse as JSON array
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                # If not JSON, treat as comma-separated string
                return [origin.strip() for origin in v.split(",")]
        return v

    @model_validator(mode="after")
    def assemble_database_url(self):
        has_db_components = all(
            [
                self.DB_HOST,
                self.DB_PORT,
                self.DB_NAME,
                self.DB_USERNAME,
                self.DB_PASSWORD,
            ]
        )
        if has_db_components:
            self.DATABASE_URL = (
                f"postgresql://{self.DB_USERNAME}:{self.DB_PASSWORD}"
                f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            )
        return self

    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Trading Simulator"

    # Trading
    MAX_ORDERS_PER_USER: int = 1000
    MAX_POSITION_SIZE: float = 1000000.0
    SESSION_DURATION_MINUTES: int = 60

    # Logging
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_FILE: Optional[str] = None  # Set to None to disable file logging

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
