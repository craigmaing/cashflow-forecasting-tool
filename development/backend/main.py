"""
Cash Flow Forecasting Tool - Main FastAPI Application
"""

import os
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from typing import Optional

# Import routers
from routers import auth, organizations, users, accounts, transactions, forecasts, integrations, alerts
from database import Database
from config import settings
from middleware.auth import verify_token
from middleware.logging import setup_logging
from middleware.rate_limiting import RateLimitingMiddleware

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Cash Flow Forecasting Tool API")
    
    # Initialize database connection
    await Database.connect()
    logger.info("Database connected successfully")
    
    # Run database migrations if needed
    # await Database.migrate()
    
    yield
    
    # Shutdown
    logger.info("Shutting down Cash Flow Forecasting Tool API")
    await Database.disconnect()

# Create FastAPI application
app = FastAPI(
    title="Cash Flow Forecasting Tool API",
    description="Enterprise-grade cash flow forecasting and financial planning platform",
    version="1.0.0",
    docs_url="/api/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/api/redoc" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan,
)

# Add security middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting middleware
app.add_middleware(RateLimitingMiddleware)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error_id": "INTERNAL_ERROR"}
    )

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        db_status = await Database.health_check()
        
        return {
            "status": "healthy",
            "version": "1.0.0",
            "environment": settings.ENVIRONMENT,
            "database": "connected" if db_status else "disconnected",
            "timestamp": Database.get_timestamp()
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unavailable"
        )

# API version endpoint
@app.get("/api/v1/version", tags=["Info"])
async def get_version():
    """Get API version information"""
    return {
        "version": "1.0.0",
        "release_date": "2025-08-03",
        "features": [
            "AI-powered forecasting",
            "Real-time data sync",
            "Multi-currency support",
            "Advanced scenarios",
            "Enterprise integrations"
        ]
    }

# Include routers with API prefix
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(organizations.router, prefix="/api/v1/organizations", tags=["Organizations"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(accounts.router, prefix="/api/v1/accounts", tags=["Bank Accounts"])
app.include_router(transactions.router, prefix="/api/v1/transactions", tags=["Transactions"])
app.include_router(forecasts.router, prefix="/api/v1/forecasts", tags=["Forecasts"])
app.include_router(integrations.router, prefix="/api/v1/integrations", tags=["Integrations"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["Alerts"])

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Cash Flow Forecasting Tool API",
        "version": "1.0.0",
        "documentation": "/api/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True,
    )
