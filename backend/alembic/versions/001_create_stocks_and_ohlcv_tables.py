"""Create stocks and ohlcv_data tables

Revision ID: 001
Revises: 
Create Date: 2026-05-04

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create stocks table
    op.create_table(
        'stocks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('ticker', sa.String(length=20), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('sector', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('ticker')
    )
    
    # Create partial index for active stocks
    op.create_index(
        'ix_stocks_ticker_active',
        'stocks',
        ['ticker'],
        postgresql_where=sa.text('deleted_at IS NULL')
    )

    # Create ohlcv_data table
    op.create_table(
        'ohlcv_data',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('stock_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('open', sa.Numeric(precision=19, scale=4), nullable=False),
        sa.Column('high', sa.Numeric(precision=19, scale=4), nullable=False),
        sa.Column('low', sa.Numeric(precision=19, scale=4), nullable=False),
        sa.Column('close', sa.Numeric(precision=19, scale=4), nullable=False),
        sa.Column('adj_close', sa.Numeric(precision=19, scale=4), nullable=False),
        sa.Column('volume', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['stock_id'], ['stocks.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('stock_id', 'date', name='uq_ohlcv_stock_date')
    )
    
    # Create index on stock_id for FK lookups
    op.create_index('ix_ohlcv_data_stock_id', 'ohlcv_data', ['stock_id'])
    
    # Create composite index on stock_id + date for time-series queries
    op.create_index(
        'ix_ohlcv_stock_date',
        'ohlcv_data',
        ['stock_id', 'date'],
        unique=True
    )
    
    # Add check constraints
    op.create_check_constraint('ck_high_ge_low', 'ohlcv_data', 'high >= low')
    op.create_check_constraint('ck_open_in_range', 'ohlcv_data', 'open >= low AND open <= high')
    op.create_check_constraint('ck_close_in_range', 'ohlcv_data', 'close >= low AND close <= high')


def downgrade() -> None:
    op.drop_table('ohlcv_data')
    op.drop_table('stocks')
