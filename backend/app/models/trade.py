"""Trade model for backtest-generated trades."""

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Trade(Base):
    """Individual simulated trade from backtest."""

    __tablename__ = "trades"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    result_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("backtest_results.id"),
        nullable=False,
        index=True,
    )
    entry_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )
    entry_price: Mapped[Decimal] = mapped_column(
        Numeric(19, 4),
        nullable=False,
    )
    exit_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )
    exit_price: Mapped[Decimal | None] = mapped_column(
        Numeric(19, 4),
        nullable=True,
    )
    position_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    position_type: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )
    pnl: Mapped[Decimal | None] = mapped_column(
        Numeric(19, 4),
        nullable=True,
    )
    pnl_pct: Mapped[Decimal | None] = mapped_column(
        Numeric(7, 4),
        nullable=True,
    )
    exit_reason: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    # Relationships
    result: Mapped["BacktestResult"] = relationship("BacktestResult", back_populates="trades")

    __table_args__ = (
        Index("ix_trades_result_date", "result_id", "entry_date"),
    )
