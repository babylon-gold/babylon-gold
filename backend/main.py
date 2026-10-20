"""Babylon AI Gold Intelligence - FastAPI backend main entry point."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from api.routes import data, signals, analysis, health
from core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager."""
    logger.info("Babylon AI Gold Intelligence backend starting...")
    yield
    logger.info("Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Babylon AI Gold Intelligence API",
    description="Professional XAU/USD intraday market analysis platform",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(health.router, prefix="/api/v1/health", tags=["health"])
app.include_router(data.router, prefix="/api/v1/data", tags=["data"])
app.include_router(signals.router, prefix="/api/v1/signals", tags=["signals"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["analysis"])


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status": "error"},
    )


@app.get("/")
async def root():
    """Root endpoint with API documentation link."""
    return {
        "service": "Babylon AI Gold Intelligence",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
        "message": "XAU/USD intraday analysis platform - No live trading, no real money operations",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
