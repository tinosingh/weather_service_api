"""
Logging configuration for the application.

This module provides a centralized logging configuration that can be used
throughout the application. It sets up console and file handlers with
consistent formatting.
"""
import logging
import logging.config
import sys
from typing import Any, Dict, Optional

from app.core.config import settings

def setup_logging() -> None:
    """
    Configure logging for the application.
    
    This function sets up logging with both console and file handlers,
    using the configuration from settings.
    """
    # Ensure logs directory exists
    logs_dir = settings.LOGS_DIR
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Define log file paths
    log_file = logs_dir / "app.log"
    error_log_file = logs_dir / "error.log"
    
    # Logging configuration
    log_config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {
                "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": """
                    asctime: %(asctime)s
                    level: %(levelname)s
                    name: %(name)s
                    message: %(message)s
                    pathname: %(pathname)s
                    funcName: %(funcName)s
                    lineno: %(lineno)d
                """,
            },
        },
        "handlers": {
            "console": {
                "level": settings.LOG_LEVEL,
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "stream": sys.stdout,
            },
            "file": {
                "level": settings.LOG_LEVEL,
                "class": "logging.handlers.RotatingFileHandler",
                "filename": str(log_file),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "formatter": "standard",
                "encoding": "utf-8",
            },
            "error_file": {
                "level": "ERROR",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": str(error_log_file),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "formatter": "standard",
                "encoding": "utf-8",
            },
        },
        "loggers": {
            "": {  # root logger
                "handlers": ["console", "file", "error_file"],
                "level": settings.LOG_LEVEL,
                "propagate": False,
            },
            "app": {
                "handlers": ["console", "file", "error_file"],
                "level": settings.LOG_LEVEL,
                "propagate": False,
            },
            "uvicorn": {
                "handlers": ["console", "file"],
                "level": settings.LOG_LEVEL,
                "propagate": False,
            },
            "sqlalchemy": {
                "handlers": ["console", "file"],
                "level": "WARNING",
                "propagate": False,
            },
        },
    }
    
    # Apply logging configuration
    logging.config.dictConfig(log_config)
    
    # Configure uvicorn logging
    logging.getLogger("uvicorn").handlers = []
    logging.getLogger("uvicorn.access").handlers = []
    
    # Set log level for all loggers
    for logger_name in ["app", "uvicorn", "uvicorn.error", "uvicorn.access"]:
        logging.getLogger(logger_name).handlers = []
        logging.getLogger(logger_name).propagate = True
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info("Logging configured successfully")
    logger.info("Log level set to %s", settings.LOG_LEVEL)
    logger.info("Application environment: %s", settings.ENVIRONMENT)

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance with the given name.
    
    Args:
        name: The name of the logger. If None, returns the root logger.
        
    Returns:
        A configured logger instance.
    """
    return logging.getLogger(name)
