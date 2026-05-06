"""Pydantic schemas for OHLCV API."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class OHLCVDataPoint(BaseModel):
    """Single OHLCV data point."""
    date: date
    open: str  # Decimal as string for precision
    high: str
    low: str
    close: str
    adj_close: str
    volume: int


class OHLCVResponse(BaseModel):
    """Response schema for OHLCV data."""
    ticker: str
    timeframe: str = "daily"
    count: int
    data: list[OHLCVDataPoint]


class OHLCVImportRequest(BaseModel):
    """Request schema for importing OHLCV data."""
    start_date: date
    end_date: date
    on_conflict: str = Field(default="skip", pattern=r"^(skip|overwrite|merge)$")
    
    @field_validator("end_date")
    @classmethod
    def validate_date_range(cls, v: date, info) -> date:
        if "start_date" in info.data and v < info.data["start_date"]:
            raise ValueError("end_date must be after start_date")
        return v


class ImportJobResponse(BaseModel):
    """Response schema for import job status."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    ticker: str
    status: str  # PENDING, RUNNING, COMPLETED, FAILED
    start_date: date
    end_date: date
    records_imported: int | None = None
    records_skipped: int | None = None
    records_updated: int | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime
