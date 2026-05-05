"""Stock API routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import StockNotFoundException
from app.core.logging import logger
from app.database import get_db
from app.schemas.stock import StockCreate, StockListResponse, StockResponse
from app.services.stock_service import StockService

router = APIRouter(prefix="/stocks", tags=["stocks"])


@router.get("", response_model=StockListResponse)
async def list_stocks(
    search: str | None = Query(None, description="Filter by ticker or name"),
    has_data: bool | None = Query(None, description="Filter by data availability"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db),
):
    """List all imported stocks with optional filtering."""
    service = StockService(session)
    stocks, total = await service.get_all(
        search=search,
        has_data=has_data,
        limit=limit,
        offset=offset,
    )
    
    return StockListResponse(
        items=[StockResponse.model_validate(s) for s in stocks],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post("", response_model=StockResponse, status_code=status.HTTP_201_CREATED)
async def create_stock(
    data: StockCreate,
    session: AsyncSession = Depends(get_db),
):
    """Create a new stock entry."""
    service = StockService(session)
    stock = await service.create(data)
    return StockResponse.model_validate(stock)


@router.get("/{ticker}", response_model=StockResponse)
async def get_stock(
    ticker: str,
    session: AsyncSession = Depends(get_db),
):
    """Get stock details by ticker."""
    service = StockService(session)
    stock = await service.get_by_ticker(ticker)
    return StockResponse.model_validate(stock)


@router.delete("/{stock_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_stock(
    stock_id: UUID,
    hard: bool = Query(False, description="Permanently delete if true"),
    session: AsyncSession = Depends(get_db),
):
    """Delete a stock (soft delete by default)."""
    service = StockService(session)
    await service.delete(stock_id, hard=hard)
    return None
