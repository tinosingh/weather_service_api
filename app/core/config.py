"""
Application configuration and environment settings.
"""
import os
import secrets
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional
from urllib.parse import urlparse

from pydantic import Field, HttpUrl, PostgresDsn, field_validator, ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Environment types
EnvironmentType = Literal["development", "staging", "production"]
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Weather Service"
    APP_VERSION: str = "0.1.0"
    DESCRIPTION: str = "Weather data aggregation and prediction service"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8101
    DEBUG_PORT: int = 8102
    RELOAD: bool = False
    WORKERS: int = 1
    
    # Environment
    ENVIRONMENT: EnvironmentType = "development"
    DEBUG: bool = True
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"
    OPENAPI_URL: str = "/openapi.json"
    
    # Security
    SECRET_KEY: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        description="Secret key for cryptographic operations"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS - Simplified configuration
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8101"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """
        Return CORS origins as a list of valid HTTP URLs.
        
        Returns:
            List of valid HTTP URLs. Returns ["*"] if no origins are configured or if "none" is specified.
        """
        if not self.BACKEND_CORS_ORIGINS or self.BACKEND_CORS_ORIGINS.strip().lower() == "none":
            return ["*"]
        
        origins = []
        for origin in self.BACKEND_CORS_ORIGINS.split(","):
            origin = origin.strip()
            if not origin:
                continue
                
            # Validate URL format
            try:
                # This will raise ValueError for invalid URLs
                parsed = urlparse(origin)
                if not all([parsed.scheme, parsed.netloc]):
                    raise ValueError("Missing scheme or netloc")
                    
                # Reconstruct URL to normalize it
                normalized = f"{parsed.scheme}://{parsed.netloc}"
                if normalized not in origins:  # Avoid duplicates
                    origins.append(normalized)
                    
            except ValueError as e:
                if self.ENVIRONMENT == "production":
                    # In production, skip invalid URLs but log the error
                    import logging
                    logging.warning(f"Invalid CORS origin '{origin}': {e}")
                # In development, you might want to raise the error for visibility
                elif self.DEBUG:
                    raise ValueError(f"Invalid CORS origin '{origin}': {e}")
        
        return origins if origins else ["*"]
    
    # Logging
    LOG_LEVEL: LogLevel = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Paths
    BASE_DIR: Path = BASE_DIR
    LOGS_DIR: Path = BASE_DIR / "logs"
    MIGRATIONS_DIR: Path = BASE_DIR / "migrations"
    
    # Database
    POSTGRES_SERVER: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "aog4_user"
    POSTGRES_PASSWORD: str = "aog4_dev_password"
    POSTGRES_DB: str = "weather_db"
    DATABASE_URL: Optional[PostgresDsn] = None
    
    # Database connection pool settings
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600
    DB_POOL_PRE_PING: bool = True
    
    # Health check settings
    HEALTH_CHECK_ENABLED: bool = True
    HEALTH_CHECK_PATH: str = "/health"
    HEALTH_CHECK_INTERVAL: int = 30  # seconds between checks
    HEALTH_CHECK_TIMEOUT: int = 5  # seconds before timing out
    HEALTH_CHECK_DEPENDENCIES: List[str] = ["database"]  # List of dependencies to check
    HEALTH_CHECK_THRESHOLD: float = 0.8  # 80% healthy threshold for degraded state
    HEALTH_CHECK_AUTH_REQUIRED: bool = False
    HEALTH_CHECK_AUTH_USERNAME: Optional[str] = None
    HEALTH_CHECK_AUTH_PASSWORD: Optional[str] = None
    HEALTH_CHECK_CACHE_TIMEOUT: int = 5  # seconds to cache health check results
    HEALTH_CHECK_LOG_FAILURES: bool = True
    
    @property
    def health_check_config(self) -> Dict[str, Any]:
        """
        Get health check configuration as a dictionary.
        
        Returns:
            Dict containing health check configuration.
        """
        return {
            "enabled": self.HEALTH_CHECK_ENABLED,
            "path": self.HEALTH_CHECK_PATH,
            "interval": self.HEALTH_CHECK_INTERVAL,
            "timeout": self.HEALTH_CHECK_TIMEOUT,
            "dependencies": self.HEALTH_CHECK_DEPENDENCIES,
            "threshold": self.HEALTH_CHECK_THRESHOLD,
            "auth_required": self.HEALTH_CHECK_AUTH_REQUIRED,
            "auth_username": self.HEALTH_CHECK_AUTH_USERNAME,
            "auth_password": self.HEALTH_CHECK_AUTH_PASSWORD,
            "cache_timeout": self.HEALTH_CHECK_CACHE_TIMEOUT,
            "log_failures": self.HEALTH_CHECK_LOG_FAILURES,
        }
    
    # Async database settings
    ASYNC_DB_ENABLED: bool = True
    ASYNC_DB_USE_CONNECTION_POOL_FOR_TESTING: bool = False
    
    # SQL logging
    SQL_ECHO: bool = False
    SQL_ECHO_POOL: bool = False
    SQL_SHOW_PARAMETERS: bool = False
    
    # FMI API
    FMI_API_KEY: Optional[str] = None
    FMI_API_URL: HttpUrl = "https://opendata.fmi.fi/wfs"
    
    # Weather data
    DEFAULT_LOCATION: str = "Kaisaniemi,Helsinki"
    DEFAULT_LATITUDE: float = 60.1699
    DEFAULT_LONGITUDE: float = 24.9384
    
    # Data retention
    DEFAULT_RETENTION_DAYS: int = 30
    
    @property
    def async_database_url(self) -> Optional[str]:
        """Get the async database URL."""
        if not self.DATABASE_URL:
            return None
        return str(self.DATABASE_URL).replace("postgresql://", "postgresql+asyncpg://")
    
    # Alias for backward compatibility
    ASYNC_DATABASE_URL = async_database_url
    
    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info: ValidationInfo) -> Any:
        """Assemble the database connection URL from components if not provided directly."""
        if isinstance(v, str):
            return v
            
        # Get the values from the model instance
        values = info.data
        
        # Build the database URL from components
        return PostgresDsn.build(
            scheme="postgresql",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            port=values.get("POSTGRES_PORT", 5432),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )
    
    @property
    def is_development(self) -> bool:
        """Check if the application is running in development mode."""
        return self.ENVIRONMENT == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if the application is running in production mode."""
        return self.ENVIRONMENT == "production"
    
    # Pydantic configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
        env_prefix="WEATHER_",
    )

# Create settings instance
@lru_cache()
def get_settings() -> Settings:
    """Get a cached instance of the settings."""
    return Settings()

# Global settings instance
settings = get_settings()

# Ensure required directories exist
os.makedirs(settings.LOGS_DIR, exist_ok=True)
os.makedirs(settings.MIGRATIONS_DIR, exist_ok=True)
