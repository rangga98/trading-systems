# Trading Simulator Constitution

## Core Principles

### I. API-First Architecture
Backend exposes REST API only — no server-side rendering.
Frontend is a pure SPA that communicates exclusively via `/api/v1/` endpoints.
Every endpoint must have Pydantic request/response schema defined before implementation.
No business logic in route handlers — use service layer.

### II. Data Integrity (NON-NEGOTIABLE)
All price and monetary values stored as `NUMERIC(19,4)` — never float or double.
OHLCV data fetched from yfinance once, persisted to PostgreSQL — never hit yfinance on every request.
All tables must have `created_at` and `updated_at` audit columns.
All tables use soft delete via `deleted_at` timestamp — no hard deletes.

### III. Test-First (NON-NEGOTIABLE)
TDD mandatory: tests written and approved before implementation code.
Red-Green-Refactor cycle strictly enforced.
Every service layer function must have unit tests.
Every API endpoint must have integration tests.

### IV. Backtest Engine Server-Side
All backtest computation runs on Python backend — never client-side JavaScript.
Backtest results are persisted to DB and retrievable via API.
Engine must be deterministic: same inputs always produce same outputs.

### V. Simplicity & YAGNI
Start with the simplest working solution.
No premature optimization — profile before optimizing.
No feature built without a corresponding spec task.

## Tech Stack

### Backend
- Python 3.12+
- FastAPI (async)
- SQLAlchemy 2.0 (async ORM)
- Alembic (migrations)
- yfinance + pandas (data fetching & manipulation)
- TA-Lib (technical indicators: MA, RSI, MACD, Bollinger Bands, dll)
  - Requires: `brew install ta-lib` on macOS before `uv add ta-lib`
- Pydantic v2 (validation)
- uv (package manager)

### Frontend
- React 18+ with Vite
- Tailwind CSS + shadcn/ui (components)
- lightweight-charts by TradingView (candlestick chart)
- Zustand (state management)
- TanStack Query (data fetching & caching)

### Infrastructure
- PostgreSQL (primary database)
- Docker Compose (local development: DB + backend + frontend)

## Naming & Language Conventions

- Code, variables, functions, DB columns: English
- UI labels, messages, tooltips: Bahasa Indonesia
- API responses: English keys, Indonesian display values where applicable
- File and folder names: kebab-case for frontend, snake_case for backend

## Development Workflow

1. Feature starts with a spec task in `tasks/`
2. Write tests first — get approval before implementing
3. Implement to make tests pass
4. API contract must match Pydantic schema — no undocumented fields
5. Run `/analyze` to validate consistency before PR

## Governance

This constitution supersedes all other conventions and preferences.
Any amendment requires: documentation of reason, update to this file, and migration plan if breaking.
All implementation must be verified against this constitution before merge.
When in doubt, refer back to the spec and plan — not to assumptions.

**Version**: 1.0.0 | **Ratified**: 2025-05-04 | **Last Amended**: 2025-05-04