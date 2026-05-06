"""Create backtest tables.

Revision ID: 002
Revises: 001
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create backtest_configs table
    op.create_table(
        'backtest_configs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('ticker', sa.String(20), nullable=False),
        sa.Column('initial_capital', sa.Numeric(19, 4), nullable=False),
        sa.Column('position_sizing_type', sa.String(20), nullable=False),
        sa.Column('position_size_value', sa.Numeric(19, 4), nullable=False),
        sa.Column('stop_loss_pct', sa.Numeric(5, 2), nullable=True),
        sa.Column('take_profit_pct', sa.Numeric(5, 2), nullable=True),
        sa.Column('entry_rules', sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column('exit_rules', sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column('date_range_start', sa.Date(), nullable=False),
        sa.Column('date_range_end', sa.Date(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    
    op.create_index('ix_backtest_configs_ticker', 'backtest_configs', ['ticker'])
    op.create_index('ix_backtest_configs_created_at', 'backtest_configs', ['created_at'])
    
    # Create backtest_results table
    op.create_table(
        'backtest_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('config_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('backtest_configs.id'), nullable=False, index=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='PENDING'),
        sa.Column('total_pnl', sa.Numeric(19, 4), nullable=True),
        sa.Column('total_return_pct', sa.Numeric(7, 4), nullable=True),
        sa.Column('win_rate', sa.Numeric(5, 2), nullable=True),
        sa.Column('total_trades', sa.Integer(), nullable=True),
        sa.Column('max_drawdown', sa.Numeric(19, 4), nullable=True),
        sa.Column('max_drawdown_pct', sa.Numeric(7, 4), nullable=True),
        sa.Column('sharpe_ratio', sa.Numeric(7, 4), nullable=True),
        sa.Column('equity_curve', sa.JSON(), nullable=True),
        sa.Column('executed_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    
    op.create_index('ix_results_config_status', 'backtest_results', ['config_id', 'status'])
    op.create_index('ix_backtest_results_status', 'backtest_results', ['status'])
    
    # Create trades table
    op.create_table(
        'trades',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('result_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('backtest_results.id'), nullable=False, index=True),
        sa.Column('entry_date', sa.Date(), nullable=False),
        sa.Column('entry_price', sa.Numeric(19, 4), nullable=False),
        sa.Column('exit_date', sa.Date(), nullable=True),
        sa.Column('exit_price', sa.Numeric(19, 4), nullable=True),
        sa.Column('position_size', sa.Integer(), nullable=False),
        sa.Column('position_type', sa.String(10), nullable=False),
        sa.Column('pnl', sa.Numeric(19, 4), nullable=True),
        sa.Column('pnl_pct', sa.Numeric(7, 4), nullable=True),
        sa.Column('exit_reason', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    
    op.create_index('ix_trades_result_date', 'trades', ['result_id', 'entry_date'])


def downgrade() -> None:
    op.drop_table('trades')
    op.drop_table('backtest_results')
    op.drop_table('backtest_configs')
