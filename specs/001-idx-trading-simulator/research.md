# Research & Technical Decisions: IDX Trading Simulator

**Phase**: 0 - Research & Unknown Resolution  
**Date**: 2026-05-04  
**Plan**: [plan.md](./plan.md)

## Decision Log

### 1. Charting Library

**Decision**: Use `lightweight-charts` by TradingView

**Rationale**:
- Industry standard for financial charting
- Native candlestick support with zoom/pan
- Excellent performance with 10k+ data points
- MIT license (free for commercial use)
- React wrapper available via `react-lightweight-charts`

**Alternatives considered**:
- **Recharts**: Too generic, not optimized for financial data
- **D3.js**: Too low-level, requires significant custom code
- **ApexCharts**: Good but heavier bundle size
- **Highcharts**: Commercial license required

### 2. Data Fetching - yfinance

**Decision**: Use `yfinance` library for Yahoo Finance data

**Rationale**:
- Free, reliable access to IDX historical data
- Native support for `.JK` suffix tickers
- Returns pandas DataFrame (easy to process)
- Handles splits and dividends via adjusted close
- Rate limiting handled internally

**Implementation notes**:
- Cache data in PostgreSQL after first fetch
- Never hit Yahoo Finance on chart render (per constitution)
- Handle rate limits gracefully with exponential backoff

### 3. Backend Framework - FastAPI

**Decision**: Use FastAPI with async SQLAlchemy

**Rationale**:
- Native Pydantic integration (constitution requirement)
- Async support for I/O-bound operations (DB, yfinance)
- Automatic OpenAPI documentation
- Excellent testing support with TestClient
- Type hints throughout

### 4. Database - PostgreSQL + asyncpg

**Decision**: PostgreSQL with SQLAlchemy 2.0 async ORM

**Rationale**:
- Proper NUMERIC/Decimal support for financial data (constitution requirement)
- Asyncpg driver for non-blocking DB operations
- Excellent time-series query performance with proper indexing
- Alembic for migration management

**Schema decisions**:
- All price columns: `NUMERIC(19,4)` (constitution)
- All audit columns: `created_at`, `updated_at`, `deleted_at`
- Index on `(ticker, date)` for OHLCV queries
- Index on `backtest_config_id` for trade lookups

### 5. State Management - Zustand + TanStack Query

**Decision**: TanStack Query for server state, Zustand for client state

**Rationale**:
- TanStack Query: Caching, background refetch, optimistic updates
- Zustand: Simple, minimal boilerplate for UI state
- Separation of concerns: server vs client state

### 6. UI Components - shadcn/ui

**Decision**: shadcn/ui with Tailwind CSS

**Rationale**:
- Copy-paste components (own your code)
- Built on Radix UI primitives (accessibility)
- Tailwind for rapid styling
- Indonesian language support via custom strings

### 7. Testing Strategy

**Backend**:
- pytest with pytest-asyncio for async tests
- Factory Boy for test data generation
- TestClient for API integration tests
- SQLite in-memory for fast unit tests (with NUMERIC support via `decimal` module)

**Frontend**:
- Vitest (fast, Vite-native)
- React Testing Library for component tests
- MSW (Mock Service Worker) for API mocking

### 8. IDX-Specific Considerations

**Ticker Format**: All IDX tickers use `.JK` suffix (e.g., `BBCA.JK`)

**Timezone**: WIB (Western Indonesia Time, UTC+7)
- Store all timestamps in UTC in database
- Convert to WIB for display
- Market hours: 09:00-15:00 WIB (Mon-Fri)

**Market Holidays**: Yahoo Finance data naturally excludes weekends and holidays; no custom calendar needed for MVP.

### 9. Backtest Engine Design

**Architecture**: Event-driven simulation

**Components**:
1. **Data Provider**: Fetches OHLCV from DB
2. **Strategy Evaluator**: Determines entry/exit signals
3. **Portfolio Manager**: Tracks cash, positions, P&L
4. **Trade Recorder**: Logs all executed trades
5. **Metrics Calculator**: Computes win rate, drawdown, Sharpe

**Determinism Guarantee**:
- Same seed → Same results
- No randomness in engine
- Fixed precision arithmetic (Decimal)

**Position Sizing Methods**:
1. Fixed amount (e.g., Rp 10.000.000 per trade)
2. Fixed percentage (e.g., 10% of capital)
3. Risk-based (e.g., risk 2% per trade, size = risk_amount / (entry - stop_loss))

### 10. Deployment Strategy

**Local Development**: Docker Compose
- PostgreSQL container
- Backend container (hot reload)
- Frontend container (Vite dev server)

**Production** (future consideration):
- Single VPS deployment
- Nginx reverse proxy
- Systemd services or Docker Compose

## Open Questions (None - All Resolved)

All technical decisions finalized. No [NEEDS CLARIFICATION] markers remain.

## References

- [lightweight-charts docs](https://tradingview.github.io/lightweight-charts/)
- [FastAPI async SQLAlchemy](https://fastapi.tiangolo.com/advanced/async-sql-databases/)
- [yfinance GitHub](https://github.com/ranaroussi/yfinance)
- [shadcn/ui](https://ui.shadcn.com/)
