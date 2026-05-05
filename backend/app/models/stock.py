"""Stock model for IDX-listed companies."""

import uuid

from sqlalchemy import Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Stock(Base):
    """Represents an IDX-listed company."""

    __tablename__ = "stocks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    ticker: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    sector: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # Relationships
    ohlcv_data: Mapped[list["OHLCVData"]] = relationship(
        "OHLCVData",
        back_populates="stock",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_stocks_ticker_active", "ticker", postgresql_where="deleted_at IS NULL"),
    )
