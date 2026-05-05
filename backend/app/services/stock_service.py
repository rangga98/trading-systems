"""Stock service for CRUD operations."""

from datetime import date
from typing import Sequence
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, StockNotFoundException
from app.core.logging import logger
from app.models.stock import Stock
from app.models.ohlcv import OHLCVData
from app.schemas.stock import StockCreate


class StockService:
    """Service for stock management."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(
        self,
        search: str | None = None,
        has_data: bool | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[Sequence[Stock], int]:
        """Get all stocks with optional filtering.
        
        Returns:
            Tuple of (stocks list, total count)
        """
        # Build query
        query = select(Stock).where(Stock.deleted_at.is_(None))
        
        if search:
            search_lower = f"%{search.lower()}%"
            query = query.where(
                func.lower(Stock.ticker).like(search_lower) |
                func.lower(Stock.name).like(search_lower)
            )
        
        # Get total count
        count_query = select(func.count(Stock.id)).where(Stock.deleted_at.is_(None))
        if search:
            count_query = count_query.where(
                func.lower(Stock.ticker).like(search_lower) |
                func.lower(Stock.name).like(search_lower)
            )
        
        total_result = await self.session.execute(count_query)
        total = total_result.scalar()
        
        # Add pagination
        query = query.offset(offset).limit(limit)
        
        result = await self.session.execute(query)
        stocks = result.scalars().all()
        
        # Enrich with data availability info
        for stock in stocks:
            stock.has_data = len(stock.ohlcv_data) > 0
            stock.data_count = len(stock.ohlcv_data)
            if stock.ohlcv_data:
                dates = [d.date for d in stock.ohlcv_data]
                stock.date_range = {
                    "start": min(dates),
                    "end": max(dates),
                }
        
        return stocks, total

    async def get_by_ticker(self, ticker: str) -> Stock:
        """Get stock by ticker."""
        result = await self.session.execute(
            select(Stock).where(
                Stock.ticker == ticker,
                Stock.deleted_at.is_(None)
            )
        )
        stock = result.scalar_one_or_none()
        
        if not stock:
            raise StockNotFoundException(ticker)
        
        return stock

    async def get_by_id(self, stock_id: UUID) -> Stock:
        """Get stock by ID."""
        result = await self.session.execute(
            select(Stock).where(
                Stock.id == stock_id,
                Stock.deleted_at.is_(None)
            )
        )
        stock = result.scalar_one_or_none()
        
        if not stock:
            raise StockNotFoundException(str(stock_id))
        
        return stock

    async def create(self, data: StockCreate) -> Stock:
        """Create a new stock."""
        # Check for existing active stock
        existing = await self.session.execute(
            select(Stock).where(
                Stock.ticker == data.ticker,
                Stock.deleted_at.is_(None)
            )
        )
        if existing.scalar_one_or_none():
            raise ConflictException(f"Stock with ticker '{data.ticker}' already exists")
        
        stock = Stock(
            ticker=data.ticker,
            name=data.name,
            sector=data.sector,
        )
        
        self.session.add(stock)
        await self.session.commit()
        await self.session.refresh(stock)
        
        logger.info(f"Created stock: {stock.ticker}")
        return stock

    async def delete(self, stock_id: UUID, hard: bool = False) -> None:
        """Delete stock (soft or hard)."""
        stock = await self.get_by_id(stock_id)
        
        if hard:
            await self.session.delete(stock)
        else:
            stock.soft_delete()
        
        await self.session.commit()
        logger.info(f"Deleted stock: {stock.ticker} (hard={hard})")
