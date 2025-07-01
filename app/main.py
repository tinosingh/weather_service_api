import logging
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
import uvicorn
from typing import Any, Dict
from datetime import datetime
from sqlalchemy.orm import Session

# Configure logging
logger = logging.getLogger(__name__)

from app.core.config import settings
from app.db import AsyncSessionLocal, SessionLocal
from app.api.v1.api import api_router

# Create database tables (in a real app, use migrations instead)

def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    # Initialize FastAPI app with metadata
    app = FastAPI(
        title=settings.APP_NAME,
        description=settings.DESCRIPTION,
        version=settings.APP_VERSION,
        docs_url=settings.DOCS_URL if settings.DEBUG else None,
        redoc_url=settings.REDOC_URL if settings.DEBUG else None,
        openapi_url=settings.OPENAPI_URL if settings.DEBUG else None,
        debug=settings.DEBUG,
    )

    # Set up CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API router
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    # Add health check endpoint with configuration from settings
    @app.get(
        settings.HEALTH_CHECK_PATH,
        tags=["health"],
        status_code=200,
        responses={
            200: {"description": "Service is healthy"},
            503: {"description": "Service is unhealthy"},
        }
    )
    async def health_check() -> Dict[str, Any]:
        """
        Health check endpoint for monitoring and readiness probes.
        
        Returns:
            Dict containing health status and component statuses.
        """
        from fastapi import HTTPException, status
        
        status_info = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "components": {}
        }
        
        # Check database connection if configured
        if "database" in settings.HEALTH_CHECK_DEPENDENCIES:
            try:
                # Test database connection
                from sqlalchemy import text
                async with AsyncSessionLocal() as session:
                    await session.execute(text("SELECT 1"))
                status_info["components"]["database"] = "ok"
            except Exception as e:
                if settings.HEALTH_CHECK_LOG_FAILURES:
                    import logging
                    logging.error(f"Database health check failed: {str(e)}")
                status_info["components"]["database"] = "error"
                status_info["status"] = "unhealthy"
        
        # Add more component checks as needed
        
        # Check if any components are unhealthy
        if any(status == "error" for status in status_info["components"].values()):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=status_info
            )
            
        return status_info

    # Add root endpoint
    @app.get("/", tags=["root"])
    async def root() -> Dict[str, Any]:
        """Root endpoint with basic application information."""
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "docs": settings.DOCS_URL if settings.DEBUG else None,
            "api_docs": f"{settings.API_V1_PREFIX}/docs" if settings.DEBUG else None,
            "status": "running",
        }

    # Database dependency
    def get_db() -> Session:
        """
        Get a database session.

        Yields:
            Session: A SQLAlchemy database session.
        """
        db = SessionLocal()
        try:
            yield db
        except Exception as e:
            logger.error(f"Database error: {str(e)}")
            db.rollback()
            raise
        finally:
            db.close()

    # Add error handlers
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc: HTTPException) -> JSONResponse:
        """Handle HTTP exceptions with consistent error format."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "status_code": exc.status_code,
            },
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc: Exception) -> JSONResponse:
        """Handle all other exceptions with a 500 status code."""
        logger.exception("Unhandled exception occurred")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Internal server error",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            },
        )

    # Store dependencies in app state for easier testing
    app.state.get_db = get_db
    
    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} initialized")
    return app

# Create application instance
app = create_application()

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/token"
)

# Run with uvicorn if executed directly
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        workers=settings.WORKERS if not settings.DEBUG else 1,
    )
