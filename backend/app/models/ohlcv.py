"""OHLCV data model for historical price data."""

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import BigInteger, CheckConstraint, Date, ForeignKey, Index, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class OHLCVData(Base):
    """Historical OHLCV price data for a stock."""

    __tablename__ = "ohlcv_data"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    stock_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("stocks.id"),
        nullable=False,
        index=True,
    )
    date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )
    open: Mapped[Decimal] = mapped_column(
        Numeric(19, 4),
        nullable=False,
    )
    high: Mapped[Decimal] = mapped_column(
        Numeric(19, 4),
        nullable=False,
    )
    low: Mapped[Decimal] = mapped_column(
        Numeric(19, 4),
        nullable=False,
    )
    close: Mapped[Decimal] = mapped_column(
        Numeric(19, 4),
        nullable=False,
    )
    adj_close: Mapped[Decimal] = mapped_column(
        Numeric(19, 4),
        nullable=False,
    )
    volume: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    # Relationships
    stock: Mapped["Stock"] = relationship("Stock", back_populates="ohlcv_data")

    __table_args__ = (
        # Composite unique index on stock_id + date
        Index("ix_ohlcv_stock_date", "stock_id", "date", unique=True),
        # Price sanity constraints
        CheckConstraint("high >= low", name="ck_high_ge_low"),
        CheckConstraint("open >= low AND open <= high", name="ck_open_in_range"),
        CheckConstraint("close >= low AND close <= high", name="ck_close_in_range"),
    )
