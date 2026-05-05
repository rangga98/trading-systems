"""OHLCV data API routes."""

from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.database import get_db
from app.schemas.ohlcv import OHLCVImportRequest, OHLCVResponse, ImportJobResponse
from app.services.ohlcv_service import OHLCVService
from app.services.stock_service import StockService

router = APIRouter(tags=["ohlcv"])


@router.get("/stocks/{ticker}/ohlcv", response_model=OHLCVResponse)
async def get_ohlcv_data(
    ticker: str,
    start_date: date | None = Query(None, description="Start date (inclusive)"),
    end_date: date | None = Query(None, description="End date (inclusive)"),
    timeframe: str = Query("daily", pattern=r"^(daily|weekly|monthly)$"),
    limit: int = Query(1000, ge=1, le=5000),
    session: AsyncSession = Depends(get_db),
):
    """Get OHLCV data for a stock with optional date filtering."""
    # Get stock
    stock_service = StockService(session)
    stock = await stock_service.get_by_ticker(ticker)
    
    # Get OHLCV data
    ohlcv_service = OHLCVService(session)
    data = await ohlcv_service.get_data(
        stock_id=stock.id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )
    
    # Convert to response format
    data_points = [
        {
            "date": d.date,
            "open": str(d.open),
            "high": str(d.high),
            "low": str(d.low),
            "close": str(d.close),
            "adj_close": str(d.adj_close),
            "volume": d.volume,
        }
        for d in data
    ]
    
    return OHLCVResponse(
        ticker=ticker,
        timeframe=timeframe,
        count=len(data_points),
        data=data_points,
    )


@router.post("/stocks/{ticker}/ohlcv/import", status_code=status.HTTP_202_ACCEPTED)
async def import_ohlcv_data(
    ticker: str,
    request: OHLCVImportRequest,
    session: AsyncSession = Depends(get_db),
):
    """Import OHLCV data from yfinance for a stock."""
    service = OHLCVService(session)
    
    result = await service.import_data(
        ticker=ticker,
        start_date=request.start_date,
        end_date=request.end_date,
        on_conflict=request.on_conflict,
    )
    
    return {
        "status": "completed",
        **result,
    }
