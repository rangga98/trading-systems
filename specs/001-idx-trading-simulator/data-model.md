# Data Model: IDX Trading Simulator

**Phase**: 1 - Design  
**Date**: 2026-05-04  
**Plan**: [plan.md](./plan.md)

## Entity Relationship Diagram

```
┌─────────────┐       ┌──────────────┐       ┌─────────────────────┐
│   Stock     │◄──────│  OHLCVData   │       │ BacktestConfig      │
├─────────────┤       ├──────────────┤       ├─────────────────────┤
│ id (PK)     │  1:N  │ id (PK)      │       │ id (PK)             │
│ ticker      │       │ stock_id(FK) │       │ name                │
│ name        │       │ date         │       │ initial_capital     │
│ sector      │       │ open         │       │ position_sizing_type│
│ created_at  │       │ high         │       │ position_size_value │
│ updated_at  │       │ low          │       │ stop_loss_pct       │
│ deleted_at  │       │ close        │       │ take_profit_pct     │
└─────────────┘       │ adj_close    │       │ entry_rules         │
                      │ volume       │       │ exit_rules          │
                      │ created_at   │       │ date_range_start    │
                      │ updated_at   │       │ date_range_end      │
                      │ deleted_at   │       │ ticker              │
                      └──────────────┘       │ created_at          │
                                             │ updated_at          │
                                             │ deleted_at          │
                                             └──────────┬──────────┘
                                                        │
                               ┌────────────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   BacktestResult    │
                    ├─────────────────────┤
                    │ id (PK)             │
                    │ config_id (FK)      │◄───────┐
                    │ status              │        │
                    │ total_pnl           │        │
                    │ total_return_pct    │        │
                    │ win_rate            │        │
                    │ total_trades        │        │
                    │ max_drawdown        │        │
                    │ max_drawdown_pct    │        │
                    │ sharpe_ratio        │        │
                    │ equity_curve (JSON) │        │
                    │ executed_at         │        │
                    │ completed_at        │        │
                    │ created_at          │        │
                    │ updated_at          │        │
                    │ deleted_at          │        │
                    └──────────┬──────────┘        │
                               │                   │
                               │ 1:N               │
                               ▼                   │
                    ┌─────────────────────┐        │
                    │       Trade         │        │
                    ├─────────────────────┤        │
                    │ id (PK)             │        │
                    │ result_id (FK)      │────────┘
                    │ entry_date          │
                    │ entry_price         │
                    │ exit_date           │
                    │ exit_price          │
                    │ position_size       │
                    │ position_type       │
                    │ pnl                 │
                    │ pnl_pct             │
                    │ exit_reason         │
                    │ created_at          │
                    │ updated_at          │
                    │ deleted_at          │
                    └─────────────────────┘
```

## Entity Specifications

### Stock

Represents an IDX-listed company.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK, auto | Internal identifier |
| ticker | VARCHAR(20) | UNIQUE, NOT NULL | e.g., "BBCA.JK" |
| name | VARCHAR(200) | NOT NULL | Company name (Bahasa Indonesia) |
| sector | VARCHAR(100) | NULL | Industry sector |
| created_at | TIMESTAMP | NOT NULL, DEFAULT now() | Audit |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT now() | Audit |
| deleted_at | TIMESTAMP | NULL | Soft delete |

**Indexes**:
- `ticker` (unique, for lookups)
- `deleted_at` (for filtering active records)

### OHLCVData

Historical price data for a stock.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK, auto | Internal identifier |
| stock_id | UUID | FK → Stock.id, NOT NULL | Relationship |
| date | DATE | NOT NULL | Trading date |
| open | NUMERIC(19,4) | NOT NULL | Opening price |
| high | NUMERIC(19,4) | NOT NULL | Day's high |
| low | NUMERIC(19,4) | NOT NULL | Day's low |
| close | NUMERIC(19,4) | NOT NULL | Closing price |
| adj_close | NUMERIC(19,4) | NOT NULL | Adjusted for splits/dividends |
| volume | BIGINT | NOT NULL | Shares traded |
| created_at | TIMESTAMP | NOT NULL, DEFAULT now() | Audit |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT now() | Audit |
| deleted_at | TIMESTAMP | NULL | Soft delete |

**Indexes**:
- `(stock_id, date)` (composite, unique, primary query pattern)
- `stock_id` (FK index)

**Constraints**:
- `high >= low` (price sanity)
- `open >= low AND open <= high` (open in range)
- `close >= low AND close <= high` (close in range)

### BacktestConfig

User-defined backtest parameters.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK, auto | Internal identifier |
| name | VARCHAR(200) | NOT NULL | User-friendly name |
| ticker | VARCHAR(20) | NOT NULL | Target stock (e.g., "BBCA.JK") |
| initial_capital | NUMERIC(19,4) | NOT NULL | Starting capital in IDR |
| position_sizing_type | VARCHAR(20) | NOT NULL | FIXED_AMOUNT, FIXED_PCT, RISK_BASED |
| position_size_value | NUMERIC(19,4) | NOT NULL | Amount, pct, or risk amount |
| stop_loss_pct | NUMERIC(5,2) | NULL | e.g., 5.00 = 5% |
| take_profit_pct | NUMERIC(5,2) | NULL | e.g., 10.00 = 10% |
| entry_rules | JSONB | NOT NULL | Strategy entry conditions |
| exit_rules | JSONB | NOT NULL | Strategy exit conditions |
| date_range_start | DATE | NOT NULL | Backtest start |
| date_range_end | DATE | NOT NULL | Backtest end |
| created_at | TIMESTAMP | NOT NULL, DEFAULT now() | Audit |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT now() | Audit |
| deleted_at | TIMESTAMP | NULL | Soft delete |

**Validation Rules**:
- `initial_capital > 0`
- `date_range_end > date_range_start`
- `stop_loss_pct > 0` (if set)
- `take_profit_pct > 0` (if set)

### BacktestResult

Summary of a backtest execution.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK, auto | Internal identifier |
| config_id | UUID | FK → BacktestConfig.id, NOT NULL | Relationship |
| status | VARCHAR(20) | NOT NULL | PENDING, RUNNING, COMPLETED, FAILED |
| total_pnl | NUMERIC(19,4) | NULL | Final profit/loss |
| total_return_pct | NUMERIC(7,4) | NULL | Percentage return |
| win_rate | NUMERIC(5,2) | NULL | e.g., 65.50 = 65.5% |
| total_trades | INTEGER | NULL | Number of trades |
| max_drawdown | NUMERIC(19,4) | NULL | Largest absolute drawdown |
| max_drawdown_pct | NUMERIC(7,4) | NULL | Largest percentage drawdown |
| sharpe_ratio | NUMERIC(7,4) | NULL | Risk-adjusted return |
| equity_curve | JSONB | NULL | Array of {date, equity} points |
| executed_at | TIMESTAMP | NOT NULL | When backtest started |
| completed_at | TIMESTAMP | NULL | When backtest finished |
| error_message | TEXT | NULL | If status = FAILED |
| created_at | TIMESTAMP | NOT NULL, DEFAULT now() | Audit |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT now() | Audit |
| deleted_at | TIMESTAMP | NULL | Soft delete |

**Indexes**:
- `config_id` (for fetching results by config)

### Trade

Individual simulated trade from backtest.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK, auto | Internal identifier |
| result_id | UUID | FK → BacktestResult.id, NOT NULL | Relationship |
| entry_date | DATE | NOT NULL | When position opened |
| entry_price | NUMERIC(19,4) | NOT NULL | Entry price |
| exit_date | DATE | NULL | When position closed (NULL if still open at end) |
| exit_price | NUMERIC(19,4) | NULL | Exit price |
| position_size | INTEGER | NOT NULL | Number of shares |
| position_type | VARCHAR(10) | NOT NULL | LONG or SHORT |
| pnl | NUMERIC(19,4) | NULL | Profit/loss (exit - entry) * size |
| pnl_pct | NUMERIC(7,4) | NULL | Percentage return on trade |
| exit_reason | VARCHAR(50) | NULL | STOP_LOSS, TAKE_PROFIT, END_OF_DATA, SIGNAL |
| created_at | TIMESTAMP | NOT NULL, DEFAULT now() | Audit |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT now() | Audit |
| deleted_at | TIMESTAMP | NULL | Soft delete |

**Indexes**:
- `result_id` (for fetching trades by result)
- `(result_id, entry_date)` (for sorted trade lists)

## State Transitions

### BacktestResult Status

```
PENDING → RUNNING → COMPLETED
                    ↓
                  FAILED
```

- **PENDING**: Queued for execution
- **RUNNING**: Currently processing
- **COMPLETED**: Successfully finished, results available
- **FAILED**: Error occurred, error_message set

## JSONB Schema Details

### entry_rules / exit_rules

```json
{
  "type": "simple",
  "condition": {
    "indicator": "PRICE",
    "operator": "ABOVE",
    "value": 7500
  }
}
```

For MVP (simple buy-and-hold or price-based):
- `type`: "simple" | "buy_and_hold"
- For simple: `condition` with indicator/operator/value
- For buy_and_hold: entry at first bar, exit at last bar

### equity_curve

```json
[
  {"date": "2020-01-02", "equity": 100000000.0000},
  {"date": "2020-01-03", "equity": 101500000.0000},
  ...
]
```

## Soft Delete Pattern

All entities implement soft delete via `deleted_at`:

- **Query active records**: `WHERE deleted_at IS NULL`
- **Query deleted records**: `WHERE deleted_at IS NOT NULL`
- **Delete operation**: `UPDATE SET deleted_at = NOW()`
- **Unique constraints**: Include `deleted_at IS NULL` condition or use partial indexes

## Database Migrations (Alembic)

Migration sequence:

1. `001_create_stocks_table.py`
2. `002_create_ohlcv_data_table.py`
3. `003_create_backtest_configs_table.py`
4. `004_create_backtest_results_table.py`
5. `005_create_trades_table.py`
