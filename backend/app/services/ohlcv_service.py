"""OHLCV service for data import and retrieval."""

from datetime import date, timedelta
from decimal import Decimal
from typing import Literal, Sequence
from uuid import UUID

import pandas as pd
from pandas import DataFrame
from sqlalchemy import and_, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, DataImportException, StockNotFoundException
from app.core.logging import logger
from app.models.ohlcv import OHLCVData
from app.models.stock import Stock
from app.services.yfinance_client import YFinanceClient

TimeframeType = Literal["daily", "weekly", "monthly"]


class OHLCVService:
    """Service for OHLCV data management."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.yf_client = YFinanceClient()

    async def get_data(
        self,
        stock_id: UUID,
        start_date: date | None = None,
        end_date: date | None = None,
        limit: int = 1000,
    ) -> Sequence[OHLCVData]:
        """Get OHLCV data for a stock with optional filtering."""
        query = select(OHLCVData).where(
            OHLCVData.stock_id == stock_id,
            OHLCVData.deleted_at.is_(None)
        )
        
        if start_date:
            query = query.where(OHLCVData.date >= start_date)
        if end_date:
            query = query.where(OHLCVData.date <= end_date)
        
        query = query.order_by(OHLCVData.date).limit(limit)
        
        result = await self.session.execute(query)
        return result.scalars().all()

    async def import_data(
        self,
        ticker: str,
        start_date: date,
        end_date: date,
        on_conflict: str = "skip",
    ) -> dict:
        """Import OHLCV data from yfinance.
        
        Args:
            ticker: Stock ticker
            start_date: Start date
            end_date: End date
            on_conflict: How to handle existing data (skip, overwrite, merge)
            
        Returns:
            Import statistics
        """
        # Get or create stock
        result = await self.session.execute(
            select(Stock).where(
                Stock.ticker == ticker,
                Stock.deleted_at.is_(None)
            )
        )
        stock = result.scalar_one_or_none()
        
        if not stock:
            # Fetch stock info and create
            info = await self.yf_client.get_stock_info(ticker)
            stock = Stock(
                ticker=info["ticker"],
                name=info["name"],
                sector=info.get("sector"),
            )
            self.session.add(stock)
            await self.session.flush()
        
        # Fetch data from yfinance
        df = await self.yf_client.fetch_ohlcv(ticker, start_date, end_date)
        
        if df.empty:
            return {
                "ticker": ticker,
                "records_imported": 0,
                "records_skipped": 0,
                "records_updated": 0,
            }
        
        # Handle conflicts
        imported = 0
        skipped = 0
        updated = 0
        
        for _, row in df.iterrows():
            row_date = row["date"]
            
            # Check for existing record
            existing_result = await self.session.execute(
                select(OHLCVData).where(
                    OHLCVData.stock_id == stock.id,
                    OHLCVData.date == row_date,
                    OHLCVData.deleted_at.is_(None)
                )
            )
            existing = existing_result.scalar_one_or_none()
            
            if existing:
                if on_conflict == "skip":
                    skipped += 1
                    continue
                elif on_conflict == "overwrite":
                    # Delete existing
                    await self.session.delete(existing)
                    await self.session.flush()
                elif on_conflict == "merge":
                    # Update if different
                    if self._is_data_different(existing, row):
                        existing.open = Decimal(str(row["open"]))
                        existing.high = Decimal(str(row["high"]))
                        existing.low = Decimal(str(row["low"]))
                        existing.close = Decimal(str(row["close"]))
                        existing.adj_close = Decimal(str(row["adj_close"]))
                        existing.volume = int(row["volume"])
                        updated += 1
                    else:
                        skipped += 1
                    continue
            
            # Create new record
            ohlcv = OHLCVData(
                stock_id=stock.id,
                date=row_date,
                open=Decimal(str(row["open"])),
                high=Decimal(str(row["high"])),
                low=Decimal(str(row["low"])),
                close=Decimal(str(row["close"])),
                adj_close=Decimal(str(row["adj_close"])),
                volume=int(row["volume"]),
            )
            self.session.add(ohlcv)
            imported += 1
        
        await self.session.commit()
        
        logger.info(
            f"Import complete for {ticker}: "
            f"{imported} imported, {skipped} skipped, {updated} updated"
        )
        
        return {
            "ticker": ticker,
            "records_imported": imported,
            "records_skipped": skipped,
            "records_updated": updated,
        }

    def _is_data_different(self, existing: OHLCVData, row: dict) -> bool:
        """Check if data is different from existing record."""
        return (
            float(existing.open) != float(row["open"]) or
            float(existing.high) != float(row["high"]) or
            float(existing.low) != float(row["low"]) or
            float(existing.close) != float(row["close"]) or
            float(existing.adj_close) != float(row["adj_close"]) or
            existing.volume != int(row["volume"])
        )

    async def get_data_with_timeframe(
        self,
        stock_id: UUID,
        start_date: date | None = None,
        end_date: date | None = None,
        timeframe: TimeframeType = "daily",
        limit: int = 1000,
        offset: int = 0,
    ) -> dict:
        """Get OHLCV data with timeframe aggregation and pagination.
        
        Args:
            stock_id: Stock UUID
            start_date: Filter start date
            end_date: Filter end date
            timeframe: Aggregation timeframe (daily, weekly, monthly)
            limit: Maximum records to return
            offset: Number of records to skip
            
        Returns:
            Dictionary with data, count, timeframe, and pagination info
        """
        # Get raw data
        query = select(OHLCVData).where(
            OHLCVData.stock_id == stock_id,
            OHLCVData.deleted_at.is_(None)
        )
        
        if start_date:
            query = query.where(OHLCVData.date >= start_date)
        if end_date:
            query = query.where(OHLCVData.date <= end_date)
        
        query = query.order_by(OHLCVData.date)
        
        result = await self.session.execute(query)
        records = result.scalars().all()
        
        if not records:
            return {
                "data": [],
                "count": 0,
                "timeframe": timeframe,
                "total_records": 0,
                "limit": limit,
                "offset": offset,
            }
        
        # Convert to DataFrame for aggregation
        df = pd.DataFrame([
            {
                "date": r.date,
                "open": float(r.open),
                "high": float(r.high),
                "low": float(r.low),
                "close": float(r.close),
                "adj_close": float(r.adj_close) if r.adj_close else float(r.close),
                "volume": r.volume,
            }
            for r in records
        ])
        
        df["date"] = pd.to_datetime(df["date"])
        df.set_index("date", inplace=True)
        
        # Aggregate by timeframe
        if timeframe == "weekly":
            df = self._aggregate_weekly(df)
        elif timeframe == "monthly":
            df = self._aggregate_monthly(df)
        # daily: keep as is
        
        # Apply pagination
        total_records = len(df)
        df = df.iloc[offset:offset + limit]
        
        # Convert back to list of dicts
        data = []
        for idx, row in df.iterrows():
            data.append({
                "date": idx.strftime("%Y-%m-%d"),
                "open": f"{row['open']:.2f}",
                "high": f"{row['high']:.2f}",
                "low": f"{row['low']:.2f}",
                "close": f"{row['close']:.2f}",
                "adj_close": f"{row['adj_close']:.2f}",
                "volume": int(row["volume"]),
            })
        
        return {
            "data": data,
            "count": len(data),
            "timeframe": timeframe,
            "total_records": total_records,
            "limit": limit,
            "offset": offset,
        }
    
    def _aggregate_weekly(self, df: DataFrame) -> DataFrame:
        """Aggregate daily data to weekly."""
        # Resample to weekly (week ending on Friday)
        weekly = df.resample("W-FRI").agg({
            "open": "first",      # First open of the week
            "high": "max",        # Max high of the week
            "low": "min",         # Min low of the week
            "close": "last",      # Last close of the week
            "adj_close": "last",  # Last adj_close of the week
            "volume": "sum",      # Sum of volumes
        })
        weekly = weekly.dropna()
        return weekly
    
    def _aggregate_monthly(self, df: DataFrame) -> DataFrame:
        """Aggregate daily data to monthly."""
        # Resample to monthly (month end)
        monthly = df.resample("ME").agg({
            "open": "first",      # First open of the month
            "high": "max",        # Max high of the month
            "low": "min",         # Min low of the month
            "close": "last",      # Last close of the month
            "adj_close": "last",  # Last adj_close of the month
            "volume": "sum",      # Sum of volumes
        })
        monthly = monthly.dropna()
        return monthly
