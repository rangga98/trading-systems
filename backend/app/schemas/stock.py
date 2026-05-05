"""Pydantic schemas for Stock API."""

from datetime import date
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.exceptions import TickerValidationException


class StockDateRange(BaseModel):
    """Date range for stock data availability."""
    start: date | None = None
    end: date | None = None


class StockBase(BaseModel):
    """Base stock schema."""
    ticker: str = Field(..., pattern=r'^[A-Z0-9]+\.JK$', description="IDX ticker with .JK suffix")
    name: str = Field(..., min_length=1, max_length=200)
    sector: str | None = Field(None, max_length=100)


class StockCreate(StockBase):
    """Request schema for creating a stock."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "ticker": "BBCA.JK",
            "name": "Bank Central Asia Tbk",
            "sector": "Financials"
        }
    })


class StockResponse(StockBase):
    """Response schema for stock data."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    has_data: bool = False
    data_count: int = 0
    date_range: StockDateRange | None = None
    created_at: str
    updated_at: str


class StockListResponse(BaseModel):
    """Paginated list of stocks."""
    items: list[StockResponse]
    total: int
    limit: int
    offset: int
