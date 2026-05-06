# Quickstart Guide: IDX Trading Simulator

**Feature**: IDX Trading Simulation Web App  
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## Prerequisites

- macOS/Linux/WSL (Windows)
- Python 3.12+
- Node.js 20+
- Docker & Docker Compose
- Git

## Initial Setup

### 1. Clone and Navigate

```bash
cd /Users/dindahadi/Desktop/Rangga/trading-system/trading-systems
```

### 2. Environment Setup

```bash
# Backend environment
cp backend/.env.example backend/.env
# Edit backend/.env with your settings

# Frontend environment
cp frontend/.env.example frontend/.env.local
```

Required environment variables:

```env
# backend/.env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/trading_sim
YFINANCE_CACHE_DIR=/tmp/yfinance
LOG_LEVEL=INFO

# frontend/.env.local
VITE_API_URL=http://localhost:8000/api/v1
```

### 3. Install Dependencies

```bash
# Backend (using uv)
cd backend
uv sync

# Frontend
cd ../frontend
npm install
```

**Note**: On macOS, install TA-Lib first:
```bash
brew install ta-lib
```

### 4. Start Database

```bash
cd /Users/dindahadi/Desktop/Rangga/trading-system/trading-systems
docker-compose up -d db
```

### 5. Run Migrations

```bash
cd backend
uv run alembic upgrade head
```

### 6. Start Development Servers

Using Docker Compose (recommended):
```bash
docker-compose up
```

Or manually:
```bash
# Terminal 1 - Backend
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### 7. Access Application

- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/docs
- API: http://localhost:8000/api/v1

## First Steps

### Import Your First Stock

1. Open the frontend at http://localhost:5173
2. Navigate to "Impor Data" (Import Data)
3. Enter ticker: `BBCA.JK`
4. Select date range: `2020-01-01` to `2024-12-31`
5. Click "Impor" and wait for completion

### View Candlestick Chart

1. Go to "Grafik" (Chart) page
2. Select `BBCA.JK` from dropdown
3. Chart renders with zoom/pan controls

### Run Your First Backtest

1. Go to "Backtest" page
2. Create new configuration:
   - Name: `BBCA Buy & Hold`
   - Ticker: `BBCA.JK`
   - Initial Capital: `100000000` (Rp 100M)
   - Position Sizing: `FIXED_PCT` - 100%
   - Strategy: `buy_and_hold`
3. Click "Jalankan Backtest" (Run Backtest)
4. View results: P&L, equity curve, win rate, max drawdown

## Common Commands

### Backend

```bash
cd backend

# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=html

# Add dependency
uv add package-name

# Generate migration
uv run alembic revision --autogenerate -m "description"

# Run migration
uv run alembic upgrade head

# Rollback migration
uv run alembic downgrade -1
```

### Frontend

```bash
cd frontend

# Run dev server
npm run dev

# Build for production
npm run build

# Run tests
npm run test

# Add component (shadcn)
npx shadcn add button

# Add dependency
npm install package-name
```

### Docker

```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop all
docker-compose down

# Reset database (WARNING: data loss)
docker-compose down -v
docker-compose up -d db
```

## Development Workflow

### 1. Test-First Development

```bash
# 1. Write test first
cd backend
# edit tests/unit/test_backtest_engine.py

# 2. Run test (should fail - RED)
uv run pytest tests/unit/test_backtest_engine.py -v

# 3. Implement to pass (GREEN)
# edit app/services/backtest_engine.py

# 4. Refactor while keeping tests passing (REFACTOR)
```

### 2. API Contract Development

1. Define Pydantic schema in `app/schemas/`
2. Implement service in `app/services/`
3. Add route in `app/api/`
4. Write integration test
5. Verify at http://localhost:8000/docs

### 3. Frontend Component Development

```bash
cd frontend

# Create new component
# edit src/components/MyComponent.tsx

# Use in page
# edit src/pages/Dashboard/Dashboard.tsx

# Storybook (if configured)
npm run storybook
```

## Troubleshooting

### Database Connection Issues

```bash
# Check database is running
docker-compose ps db

# Check logs
docker-compose logs db

# Reset database
docker-compose down -v
docker-compose up -d db
uv run alembic upgrade head
```

### yfinance Rate Limiting

```bash
# Add to backend/.env
YFINANCE_DELAY=1  # Seconds between requests
YFINANCE_RETRIES=3
```

### Port Conflicts

```bash
# Check what's using port 8000
lsof -i :8000

# Change ports in docker-compose.yml or .env
```

### Frontend API Connection

```bash
# Verify VITE_API_URL is set
cat frontend/.env.local

# Check browser console for CORS errors
# Backend CORS is configured for localhost:5173 by default
```

## Project Structure Reference

```
backend/
├── app/
│   ├── api/          # Route handlers
│   ├── services/     # Business logic
│   ├── models/       # SQLAlchemy ORM
│   ├── schemas/      # Pydantic validation
│   └── core/         # Config, exceptions
├── tests/
│   ├── unit/         # Service tests
│   └── integration/  # API tests
└── alembic/          # Migrations

frontend/
├── src/
│   ├── components/   # Reusable UI
│   ├── pages/        # Route pages
│   ├── services/     # API clients
│   ├── stores/       # Zustand state
│   └── types/        # TypeScript
└── tests/

specs/001-idx-trading-simulator/
├── spec.md           # Feature specification
├── plan.md           # This plan
├── research.md       # Tech decisions
├── data-model.md     # Database schema
├── contracts/        # API contracts
└── quickstart.md     # This file
```

## Next Steps

After setup:

1. Review [spec.md](./spec.md) for feature requirements
2. Check [data-model.md](./data-model.md) for database structure
3. See [contracts/](./contracts/) for API details
4. Run `/speckit.tasks` to generate implementation tasks

## Support

- API documentation: http://localhost:8000/docs
- Constitution rules: `../.specify/memory/constitution.md`
- Feature spec: [spec.md](./spec.md)
