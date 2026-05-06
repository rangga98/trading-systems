# IDX Trading Simulator - Backend

FastAPI-based backend for Indonesian Stock Exchange (IDX) trading simulation.

## Architecture

```
app/
├── api/              # REST API route handlers
├── core/             # Exceptions, logging, utilities
├── models/           # SQLAlchemy ORM models
├── schemas/          # Pydantic request/response validation
├── services/         # Business logic layer
├── database.py       # Async database connection
├── config.py         # Environment-based configuration
└── main.py           # FastAPI application entry point
```

## Setup

### 1. Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Database Migration

```bash
alembic upgrade head
```

### 4. Run Server

```bash
uvicorn app.main:app --reload
```

Server runs at `http://localhost:8000`
API docs at `http://localhost:8000/docs`

## API Endpoints

### Stocks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/stocks` | List all stocks (paginated) |
| POST | `/api/v1/stocks` | Create a new stock |
| GET | `/api/v1/stocks/{ticker}` | Get stock by ticker |
| DELETE | `/api/v1/stocks/{ticker}` | Delete a stock |
| GET | `/api/v1/stocks/search` | Search stocks by name/ticker |

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/stocks?limit=10&offset=0"
```

### OHLCV Data

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/stocks/{ticker}/ohlcv` | Get OHLCV data with timeframe aggregation |
| POST | `/api/v1/stocks/{ticker}/ohlcv/import` | Import OHLCV from yfinance |

**Query Parameters for GET:**
- `timeframe`: `daily` | `weekly` | `monthly` (default: `daily`)
- `start_date`: `YYYY-MM-DD`
- `end_date`: `YYYY-MM-DD`
- `limit`: max rows (default: 1000)
- `offset`: pagination offset (default: 0)

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/stocks/BBCA.JK/ohlcv?timeframe=weekly&start_date=2020-01-01&end_date=2024-12-31"
```

### Import Jobs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/import/jobs` | List import jobs |
| GET | `/api/v1/import/jobs/{job_id}` | Get import job status |
| POST | `/api/v1/import/bulk` | Start bulk import for multiple tickers |

### Backtest

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/backtests` | Create backtest configuration |
| GET | `/api/v1/backtests` | List configurations |
| GET | `/api/v1/backtests/{config_id}` | Get configuration |
| PATCH | `/api/v1/backtests/{config_id}` | Update configuration |
| DELETE | `/api/v1/backtests/{config_id}` | Delete configuration |
| POST | `/api/v1/backtests/{config_id}/execute` | Run backtest |
| GET | `/api/v1/backtests/results` | List results |
| GET | `/api/v1/backtests/results/{result_id}` | Get result with trades |

**Example - Create Config:**
```bash
curl -X POST "http://localhost:8000/api/v1/backtests" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Buy and Hold BBCA",
    "ticker": "BBCA.JK",
    "initial_capital": "100000000.00",
    "position_sizing_type": "FIXED_AMOUNT",
    "position_size_value": "100000000.00",
    "stop_loss_pct": 5.0,
    "take_profit_pct": 10.0,
    "date_range_start": "2020-01-01",
    "date_range_end": "2024-12-31"
  }'
```

### Export

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/backtests/results/{result_id}/export?format=csv` | Download CSV export |
| GET | `/api/v1/backtests/results/{result_id}/export?format=json` | Download JSON export |

### Health Check

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Service health status |
| GET | `/` | API info |

## Models

### Position Sizing Types
- `FIXED_AMOUNT` - Fixed Rupiah amount per trade
- `FIXED_PCT` - Percentage of capital per trade
- `RISK_BASED` - Risk-based sizing (% of capital at risk)

### Backtest Status
- `PENDING` - Queued for execution
- `RUNNING` - Currently executing
- `COMPLETED` - Successfully finished
- `FAILED` - Error during execution

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_backtest_engine.py
```
