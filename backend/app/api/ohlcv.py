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
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db),
):
    """Get OHLCV data for a stock with optional date filtering and timeframe aggregation."""
    # Get stock
    stock_service = StockService(session)
    stock = await stock_service.get_by_ticker(ticker)
    
    # Get OHLCV data with timeframe aggregation
    ohlcv_service = OHLCVService(session)
    result = await ohlcv_service.get_data_with_timeframe(
        stock_id=stock.id,
        start_date=start_date,
        end_date=end_date,
        timeframe=timeframe,  # type: ignore
        limit=limit,
        offset=offset,
    )
    
    return OHLCVResponse(
        ticker=ticker,
        timeframe=result["timeframe"],
        count=result["count"],
        data=result["data"],
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
