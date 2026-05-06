"""Backtest result model."""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Index, Integer, JSON, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class BacktestResult(Base):
    """Summary of a backtest execution."""

    __tablename__ = "backtest_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    config_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("backtest_configs.id"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="PENDING",
    )
    total_pnl: Mapped[Decimal | None] = mapped_column(
        Numeric(19, 4),
        nullable=True,
    )
    total_return_pct: Mapped[Decimal | None] = mapped_column(
        Numeric(7, 4),
        nullable=True,
    )
    win_rate: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )
    total_trades: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    max_drawdown: Mapped[Decimal | None] = mapped_column(
        Numeric(19, 4),
        nullable=True,
    )
    max_drawdown_pct: Mapped[Decimal | None] = mapped_column(
        Numeric(7, 4),
        nullable=True,
    )
    sharpe_ratio: Mapped[Decimal | None] = mapped_column(
        Numeric(7, 4),
        nullable=True,
    )
    equity_curve: Mapped[list[dict] | None] = mapped_column(
        JSON,
        nullable=True,
    )
    executed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    error_message: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # Relationships
    config: Mapped["BacktestConfig"] = relationship("BacktestConfig", back_populates="results")
    trades: Mapped[list["Trade"]] = relationship(
        "Trade",
        back_populates="result",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_results_config_status", "config_id", "status"),
    )
