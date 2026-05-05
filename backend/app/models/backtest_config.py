"""Backtest configuration model."""

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, JSON, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class BacktestConfig(Base):
    """User-defined backtest configuration."""

    __tablename__ = "backtest_configs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    ticker: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    initial_capital: Mapped[Decimal] = mapped_column(
        Numeric(19, 4),
        nullable=False,
    )
    position_sizing_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    position_size_value: Mapped[Decimal] = mapped_column(
        Numeric(19, 4),
        nullable=False,
    )
    stop_loss_pct: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )
    take_profit_pct: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )
    entry_rules: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )
    exit_rules: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )
    date_range_start: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )
    date_range_end: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    # Relationships
    results: Mapped[list["BacktestResult"]] = relationship(
        "BacktestResult",
        back_populates="config",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
