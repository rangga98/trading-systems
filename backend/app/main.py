"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.core.exceptions import AppException
from app.core.logging import logger
from app.core.middleware import RequestLoggingMiddleware
from app.api import stocks, ohlcv, import_jobs, backtest, export


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Starting up IDX Trading Simulator API")
    yield
    logger.info("Shutting down IDX Trading Simulator API")


app = FastAPI(
    title=settings.APP_NAME,
    description="Indonesian Stock Exchange Trading Simulation API",
    version="0.1.0",
    lifespan=lifespan,
)

# Request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-Duration"],
)

# Include routers
app.include_router(stocks.router, prefix=settings.API_V1_PREFIX)
app.include_router(ohlcv.router, prefix=settings.API_V1_PREFIX)
app.include_router(import_jobs.router, prefix=settings.API_V1_PREFIX)
app.include_router(backtest.router, prefix=settings.API_V1_PREFIX)
app.include_router(export.router, prefix=settings.API_V1_PREFIX)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring.

    Returns service status and basic metrics.
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": "0.1.0",
        "timestamp": __import__('datetime').datetime.now(__import__('zoneinfo').ZoneInfo(settings.TIMEZONE)).isoformat(),
    }
