"""Pydantic schemas for backtest API."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator


class BacktestConfigCreate(BaseModel):
    """Schema for creating a backtest configuration."""

    name: str = Field(..., min_length=1, max_length=200)
    ticker: str = Field(..., pattern=r"^[A-Z0-9]+\.JK$")
    initial_capital: Decimal = Field(..., gt=0, decimal_places=2)
    position_sizing_type: str = Field(..., pattern=r"^(FIXED_AMOUNT|FIXED_PCT|RISK_BASED)$")
    position_size_value: Decimal = Field(..., gt=0, decimal_places=2)
    stop_loss_pct: Decimal | None = Field(None, ge=0, le=100, decimal_places=2)
    take_profit_pct: Decimal | None = Field(None, ge=0, le=1000, decimal_places=2)
    entry_rules: dict = Field(default_factory=dict)
    exit_rules: dict = Field(default_factory=dict)
    date_range_start: date
    date_range_end: date

    @field_validator("date_range_end")
    @classmethod
    def validate_date_range(cls, v: date, info) -> date:
        """Validate date range."""
        if "date_range_start" in info.data and v < info.data["date_range_start"]:
            raise ValueError("end date must be after start date")
        return v

    @field_validator("take_profit_pct")
    @classmethod
    def validate_sl_tp(cls, v: Decimal | None, info) -> Decimal | None:
        """Validate stop loss < take profit."""
        if v is not None and "stop_loss_pct" in info.data:
            sl = info.data["stop_loss_pct"]
            if sl is not None and v <= sl:
                raise ValueError("take profit must be greater than stop loss")
        return v


class BacktestConfigUpdate(BaseModel):
    """Schema for updating a backtest configuration."""

    name: str | None = Field(None, min_length=1, max_length=200)
    initial_capital: Decimal | None = Field(None, gt=0, decimal_places=2)
    position_size_value: Decimal | None = Field(None, gt=0, decimal_places=2)
    stop_loss_pct: Decimal | None = Field(None, ge=0, le=100, decimal_places=2)
    take_profit_pct: Decimal | None = Field(None, ge=0, le=1000, decimal_places=2)
    entry_rules: dict | None = None
    exit_rules: dict | None = None


class BacktestConfigResponse(BaseModel):
    """Schema for backtest configuration response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    ticker: str
    initial_capital: Decimal
    position_sizing_type: str
    position_size_value: Decimal
    stop_loss_pct: Decimal | None
    take_profit_pct: Decimal | None
    entry_rules: dict
    exit_rules: dict
    date_range_start: date
    date_range_end: date
    created_at: datetime
    updated_at: datetime

    @field_serializer("initial_capital", "position_size_value")
    def serialize_decimal(self, v: Decimal) -> str:
        return f"{v:.2f}"


class BacktestConfigList(BaseModel):
    """Schema for paginated backtest config list."""

    total: int
    items: list[BacktestConfigResponse]


class BacktestResultResponse(BaseModel):
    """Schema for backtest result response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    config_id: UUID
    status: str
    total_pnl: Decimal | None
    total_return_pct: Decimal | None
    win_rate: Decimal | None
    total_trades: int | None
    max_drawdown: Decimal | None
    max_drawdown_pct: Decimal | None
    sharpe_ratio: Decimal | None
    equity_curve: list[dict] | None
    executed_at: datetime
    completed_at: datetime | None
    error_message: str | None
    created_at: datetime

    @field_serializer("total_pnl", "max_drawdown")
    def serialize_decimal_str(self, v: Decimal | None) -> str | None:
        return str(v) if v is not None else None


class BacktestResultDetail(BacktestResultResponse):
    """Schema for detailed backtest result with trades."""

    trades: list["TradeResponse"] = []


class TradeResponse(BaseModel):
    """Schema for trade response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    entry_date: date
    entry_price: str
    exit_date: date | None
    exit_price: str | None
    position_size: int
    position_type: str
    pnl: str | None
    pnl_pct: Decimal | None
    exit_reason: str | None


class BacktestResultList(BaseModel):
    """Schema for paginated backtest result list."""

    total: int
    items: list[BacktestResultResponse]


class BacktestExecuteRequest(BaseModel):
    """Schema for executing a backtest."""

    config_id: UUID


class BacktestExecuteResponse(BaseModel):
    """Schema for backtest execution response."""

    status: str
    result_id: UUID | None = None
    message: str | None = None
