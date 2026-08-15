import logging
from datetime import datetime, timezone
from fastapi import FastAPI, Depends, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    generic_exception_handler,
)
from app.api.v1.router import api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.ENVIRONMENT == "production" else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("faculty_scheduler")

# Create FastAPI application
app = FastAPI(
    title="Faculty Availability & Appointment Scheduler API",
    description=(
        "Backend REST API for the Faculty Availability & Appointment Scheduler. "
        "Provides dynamic scheduling, role-based access control, and appointment lifecycle workflows."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Global Exception Handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
if settings.ENVIRONMENT == "production":
    app.add_exception_handler(Exception, generic_exception_handler)

# Include API Routers
app.include_router(api_router)


# Health Check Endpoints
@app.get("/health", tags=["Health"], status_code=status.HTTP_200_OK)
def health_check():
    """System health check endpoint."""
    return {
        "status": "healthy",
        "service": "Faculty Availability Scheduler API",
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/health/db", tags=["Health"], status_code=status.HTTP_200_OK)
def db_health_check(response: Response, db: Session = Depends(get_db)):
    """Database connectivity health check endpoint."""
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "connected",
            "database": "operational",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {
            "status": "error",
            "database": "unreachable",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


@app.get("/", tags=["Root"])
def root():
    """Root welcoming endpoint with links to OpenAPI documentation."""
    return {
        "message": "Welcome to Faculty Availability & Appointment Scheduler API",
        "docs_url": "/docs",
        "version": "1.0.0",
    }
