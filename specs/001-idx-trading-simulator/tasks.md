# Tasks: IDX Trading Simulation Web App

**Input**: Design documents from `/specs/001-idx-trading-simulator/`  
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/, quickstart.md  
**Tests**: Included per constitution TDD requirement

**Organization**: Tasks grouped by user story for independent implementation and testing.

**Format**: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story label (US1, US2, US3, US4)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 [P] Create backend project structure with `backend/app/` directories (models, schemas, services, api, core)
- [x] T002 [P] Create frontend project structure with `frontend/src/` directories (components, pages, services, stores, types)
- [x] T003 Initialize backend with `pyproject.toml`, FastAPI, SQLAlchemy 2.0, asyncpg, yfinance, pandas, pydantic, pytest
- [x] T004 Initialize frontend with Vite, React 18, TypeScript, Tailwind CSS, shadcn/ui, TanStack Query, Zustand, lightweight-charts
- [x] T005 [P] Configure backend linting (ruff) and formatting (ruff format)
- [x] T006 [P] Configure frontend linting (ESLint) and formatting (Prettier)
- [x] T007 Create root `docker-compose.yml` with PostgreSQL, backend, and frontend services

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Backend Foundation

- [x] T008 Create `backend/app/config.py` with Pydantic settings (DATABASE_URL, yfinance config, timezone)
- [x] T009 Create `backend/app/database.py` with async SQLAlchemy engine, session, and base model with audit columns
- [x] T010 Create `backend/app/core/exceptions.py` with custom exception classes (StockNotFound, ValidationError, etc.)
- [x] T011 Create `backend/app/core/logging.py` with structured logging configuration
- [x] T012 Create `backend/alembic.ini` and initialize migration environment

### Frontend Foundation

- [x] T013 Create `frontend/src/services/api.ts` with Axios instance and TanStack Query client setup
- [x] T014 Create `frontend/src/stores/appStore.ts` with Zustand for global UI state
- [x] T015 Create `frontend/src/types/index.ts` with shared TypeScript interfaces matching API schemas
- [x] T016 Configure Tailwind CSS with custom colors and shadcn/ui theme

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Import Historical Stock Data (Priority: P1) 🎯 MVP

**Goal**: Enable users to import OHLCV data from yfinance and store in PostgreSQL with conflict handling

**Independent Test**: Enter ticker "BBCA.JK" with date range, verify data appears in database, can view in table

### Tests for User Story 1 ⚠️ (Write FIRST - must FAIL before implementation)

- [x] T017 [P] [US1] Write unit test for yfinance client in `backend/tests/unit/test_yfinance_client.py`
- [x] T018 [P] [US1] Write unit test for OHLCV import service in `backend/tests/unit/test_ohlcv_service.py`
- [x] T019 [P] [US1] Write integration test for stock import endpoint in `backend/tests/integration/test_stocks_api.py`
- [x] T020 [P] [US1] Write integration test for OHLCV import endpoint in `backend/tests/integration/test_ohlcv_api.py`

### Backend Implementation - User Story 1

- [x] T021 [P] [US1] Create `Stock` model in `backend/app/models/stock.py` with audit columns and soft delete
- [x] T022 [P] [US1] Create `OHLCVData` model in `backend/app/models/ohlcv.py` with NUMERIC(19,4) prices, indexes on (stock_id, date)
- [x] T023 [US1] Create Alembic migration `001_create_stocks_and_ohlcv_tables.py` (depends on T021, T022)
- [x] T024 [P] [US1] Create `StockSchema` Pydantic schemas in `backend/app/schemas/stock.py`
- [x] T025 [P] [US1] Create `OHLCVSchema` Pydantic schemas in `backend/app/schemas/ohlcv.py`
- [x] T026 [US1] Implement `YFinanceClient` in `backend/app/services/yfinance_client.py` with rate limiting (depends on T017)
- [x] T027 [US1] Implement `StockService` in `backend/app/services/stock_service.py` with CRUD operations
- [x] T028 [US1] Implement `OHLCVService` in `backend/app/services/ohlcv_service.py` with import logic and conflict handling (depends on T026)
- [x] T029 [US1] Implement stocks API routes in `backend/app/api/stocks.py` with list, get, create, delete endpoints
- [x] T030 [US1] Implement OHLCV API routes in `backend/app/api/ohlcv.py` with get data and import endpoints (depends on T028)
- [x] T031 [US1] Add import job tracking table and endpoints for async progress feedback
- [x] T032 [US1] Add IDX-specific ticker validation (.JK suffix) in schemas
- [x] T033 [US1] Add WIB timezone handling in datetime utilities
- [x] T034 [US1] Register routes in `backend/app/main.py` with `/api/v1` prefix

### Frontend Implementation - User Story 1

- [x] T035 [P] [US1] Create stock API client functions in `frontend/src/services/stocks.ts`
- [x] T036 [P] [US1] Create OHLCV API client functions in `frontend/src/services/ohlcv.ts`
- [x] T037 [US1] Create `StockImportForm` component in `frontend/src/components/StockImportForm.tsx` with ticker validation
- [x] T038 [US1] Create `ImportProgress` component in `frontend/src/components/ImportProgress.tsx` for job status
- [x] T039 [US1] Create `DataTable` component in `frontend/src/components/DataTable.tsx` for viewing OHLCV data
- [x] T040 [US1] Create `StockListPage` in `frontend/src/pages/StockImport/StockListPage.tsx` with search/filter
- [x] T041 [US1] Create `StockImportPage` in `frontend/src/pages/StockImport/StockImportPage.tsx` with form
- [x] T042 [US1] Create `OHLCVViewPage` in `frontend/src/pages/StockImport/OHLCVViewPage.tsx` with data table
- [x] T043 [US1] Add routes in `frontend/src/App.tsx` for import flow

**Checkpoint**: User Story 1 complete - users can import stocks and view OHLCV data

---

## Phase 4: User Story 2 - Visualize Candlestick Charts (Priority: P1)

**Goal**: Display interactive candlestick charts with zoom, pan, and timeframe selection

**Independent Test**: Select imported ticker, verify candlestick chart renders with smooth zoom/pan

### Tests for User Story 2 ⚠️ (Write FIRST)

- [x] T044 [P] [US2] Write integration test for OHLCV data aggregation by timeframe in backend

### Backend Implementation - User Story 2

- [x] T045 [US2] Extend `OHLCVService` in `backend/app/services/ohlcv_service.py` with timeframe aggregation (daily→weekly→monthly)
- [x] T046 [US2] Add timeframe parameter support to `backend/app/api/ohlcv.py` endpoints
- [x] T047 [US2] Optimize OHLCV queries with pagination for large datasets (1000+ rows)

### Frontend Implementation - User Story 2

- [x] T048 [US2] Install and configure `lightweight-charts` package in frontend
- [x] T049 [US2] Create `CandlestickChart` component in `frontend/src/components/Chart/CandlestickChart.tsx` with lightweight-charts
- [x] T050 [US2] Add chart configuration: price scale, time scale, candlestick series
- [x] T051 [US2] Implement zoom and pan handling with mouse/trackpad
- [x] T052 [US2] Create timeframe selector component in `frontend/src/components/Chart/TimeframeSelector.tsx`
- [x] T053 [US2] Implement timeframe switching logic with data refetching
- [x] T054 [US2] Add loading states and error handling for chart data
- [x] T055 [US2] Create `ChartViewPage` in `frontend/src/pages/ChartView/ChartViewPage.tsx` with ticker selector and chart
- [x] T056 [US2] Add responsive chart sizing for different screen widths
- [x] T057 [US2] Add route for chart view in `frontend/src/App.tsx`

**Checkpoint**: User Story 2 complete - users can view interactive candlestick charts

---

## Phase 5: User Story 3 - Execute Backtesting (Priority: P1)

**Goal**: Run backtests with money management and display P&L, equity curve, metrics

**Independent Test**: Configure buy-and-hold with Rp 100M capital, verify results show P&L, equity curve, win rate, max drawdown

### Tests for User Story 3 ⚠️ (Write FIRST)

- [x] T058 [P] [US3] Write unit test for backtest engine calculation accuracy in `backend/tests/unit/test_backtest_engine.py`
- [x] T059 [P] [US3] Write unit test for position sizing strategies in `backend/tests/unit/test_position_sizing.py`
- [x] T060 [P] [US3] Write integration test for backtest API endpoints in `backend/tests/integration/test_backtest_api.py`

### Backend Implementation - User Story 3

- [x] T061 [P] [US3] Create `BacktestConfig` model in `backend/app/models/backtest_config.py`
- [x] T062 [P] [US3] Create `BacktestResult` model in `backend/app/models/backtest_result.py`
- [x] T063 [P] [US3] Create `Trade` model in `backend/app/models/trade.py`
- [x] T064 [US3] Create Alembic migration `002_create_backtest_tables.py` (depends on T061-T063)
- [x] T065 [P] [US3] Create `BacktestSchema` Pydantic schemas in `backend/app/schemas/backtest.py` with proper Decimal handling
- [x] T066 [US3] Implement `BacktestEngine` in `backend/app/services/backtest_engine.py` with:
  - Event-driven simulation loop
  - Portfolio tracking (cash, positions, equity)
  - Position sizing: FIXED_AMOUNT, FIXED_PCT, RISK_BASED
  - Stop loss and take profit logic
  - Buy-and-hold strategy implementation
  - Deterministic execution (same inputs = same outputs)
- [x] T067 [US3] Implement `MetricsCalculator` in `backend/app/services/metrics_calculator.py` for:
  - Total P&L and return percentage
  - Win rate calculation
  - Max drawdown (absolute and percentage)
  - Sharpe ratio
  - Equity curve generation
- [x] T068 [US3] Implement `BacktestService` in `backend/app/services/backtest_service.py` with config CRUD and execution (depends on T066, T067)
- [x] T069 [US3] Implement backtest API routes in `backend/app/api/backtest.py` with:
  - CRUD for configurations
  - Execute endpoint (returns result ID)
  - Get result with trades endpoint
  - List results with filtering/sorting
- [x] T070 [US3] Add validation for money management parameters (stop_loss < take_profit, positive capital, etc.)
- [x] T071 [US3] Add backtest status tracking (PENDING, RUNNING, COMPLETED, FAILED) with error handling
- [x] T072 [US3] Register backtest routes in `backend/app/main.py`

### Frontend Implementation - User Story 3

- [x] T073 [P] [US3] Create backtest API client functions in `frontend/src/services/backtest.ts`
- [x] T074 [US3] Create `BacktestConfigForm` component in `frontend/src/components/BacktestForm/BacktestConfigForm.tsx` with:
  - Strategy name input
  - Initial capital (Rp amount as string for precision)
  - Position sizing type selector and value input
  - Stop loss and take profit percentages
  - Date range picker
- [x] T075 [US3] Create `BacktestResultsTable` component in `frontend/src/components/BacktestForm/BacktestResultsTable.tsx` with sortable metrics
- [x] T076 [US3] Create `EquityCurveChart` component in `frontend/src/components/Chart/EquityCurveChart.tsx` using lightweight-charts
- [x] T077 [US3] Create `TradeHistoryTable` component in `frontend/src/components/BacktestForm/TradeHistoryTable.tsx`
- [x] T078 [US3] Create `BacktestRunPage` in `frontend/src/pages/Backtest/BacktestRunPage.tsx` with config form and run button
- [x] T079 [US3] Create `BacktestResultsPage` in `frontend/src/pages/Backtest/BacktestResultsPage.tsx` with results table and comparison
- [x] T080 [US3] Create `BacktestDetailPage` in `frontend/src/pages/Backtest/BacktestDetailPage.tsx` with equity curve and trade history
- [x] T081 [US3] Add backtest routes in `frontend/src/App.tsx`

**Checkpoint**: User Story 3 complete - users can run backtests and view comprehensive results

---

## Phase 6: User Story 4 - Export Backtest Results (Priority: P2)

**Goal**: Export backtest results and trade history to CSV format

**Independent Test**: Click export on completed backtest, verify CSV downloads with correct trade details

### Tests for User Story 4 ⚠️ (Write FIRST)

- [x] T082 [P] [US4] Write unit test for CSV export service in `backend/tests/unit/test_export_service.py`

### Backend Implementation - User Story 4

- [x] T083 [US4] Implement `ExportService` in `backend/app/services/export_service.py` with CSV generation (depends on T082)
- [x] T084 [US4] Create CSV format with summary header and trades detail rows
- [x] T085 [US4] Implement export API routes in `backend/app/api/export.py` with CSV download endpoint
- [x] T086 [US4] Add JSON export endpoint for programmatic access
- [x] T087 [US4] Register export routes in `backend/app/main.py`

### Frontend Implementation - User Story 4

- [x] T088 [P] [US4] Create export API client functions in `frontend/src/services/export.ts`
- [x] T089 [US4] Create `ExportButton` component in `frontend/src/components/ExportButton.tsx` with format selector
- [x] T090 [US4] Add export functionality to `BacktestDetailPage`
- [x] T091 [US4] Implement CSV download with proper filename (e.g., `backtest_bbcajk_20200102_20241230.csv`)

**Checkpoint**: User Story 4 complete - users can export backtest results to CSV

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

### Documentation & Validation

- [ ] T092 [P] Create comprehensive API documentation in `backend/README.md` with endpoint examples
- [ ] T093 [P] Create frontend component documentation in `frontend/README.md`
- [ ] T094 Validate `quickstart.md` setup instructions by running through fresh clone
- [ ] T095 [P] Add `.env.example` files for both backend and frontend

### Error Handling & UX

- [ ] T096 Add global error boundary in frontend with user-friendly error messages
- [ ] T097 Add toast notification system for async operations (import complete, backtest complete)
- [ ] T098 Add loading skeletons for all data-fetching components
- [ ] T099 Add empty states for lists with no data

### Performance & Optimization

- [ ] T100 Add database query optimization (review slow queries, add missing indexes)
- [ ] T101 Add frontend bundle optimization (lazy loading for pages)
- [ ] T102 Add TanStack Query caching strategy with proper invalidation

### Security & Robustness

- [ ] 103 [P] Add input sanitization and validation on all API endpoints
- [ ] T104 Add CORS configuration for production
- [ ] T105 Add health check endpoint for monitoring
- [ ] T106 Add request logging middleware

**Final Checkpoint**: All user stories complete, documentation validated, ready for deployment

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup) → Phase 2 (Foundational) → Phase 3-6 (User Stories in parallel) → Phase 7 (Polish)
```

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational, can run in parallel:
  - US1: Data Import (P1)
  - US2: Candlestick Charts (P1)
  - US3: Backtesting (P1)
  - US4: Export (P2)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### Story Dependencies

| Story | Depends On | Notes |
|-------|------------|-------|
| US1 | Foundational | No other story dependencies - can be MVP alone |
| US2 | Foundational + US1 | Needs imported data to display charts |
| US3 | Foundational + US1 | Needs OHLCV data for backtesting |
| US4 | Foundational + US3 | Needs completed backtest results to export |

### Within Each User Story

```
Tests (parallel) → Models (parallel) → Migration → Services → API Routes → Frontend Components → Pages → Routes
```

### Parallel Opportunities

With multiple developers after Phase 2 completes:

**Developer A - Backend Focus**:
- T026-T034 (yfinance client, stock/OHLCV services, routes)
- T058-T072 (backtest engine, metrics, services, routes)

**Developer B - Frontend Focus**:
- T035-T043 (stock import UI)
- T048-T057 (chart visualization)
- T073-T081 (backtest UI)

**Developer C - Integration & Tests**:
- T017-T020, T044, T058-T060, T082 (all tests)
- T092-T106 (polish, docs, validation)

---

## Implementation Strategy

### MVP First (Recommended)

1. **Complete Phase 1**: Setup (T001-T007)
2. **Complete Phase 2**: Foundational (T008-T016) - **CRITICAL PATH**
3. **Complete Phase 3**: User Story 1 - Data Import (T017-T043)
4. **STOP & VALIDATE**: Test import independently
5. **Demo/Deploy**: MVP with data import capability

### Incremental Delivery

After MVP foundation (Phase 1-2 complete):

| Phase | Deliverable | Test Criteria |
|-------|-------------|---------------|
| US1 | Data Import | Import BBCA.JK, view in table |
| US2 | Charts | Select BBCA.JK, see candlesticks, zoom/pan |
| US3 | Backtest | Run buy-and-hold, see P&L + equity curve |
| US4 | Export | Download CSV, verify in Excel |

### Priority-Based Sequencing (Single Developer)

```
T001-T016 (Setup + Foundational)
  ↓
T017-T043 (US1: Data Import) - MVP READY
  ↓
T044-T057 (US2: Charts)
  ↓
T058-T081 (US3: Backtest)
  ↓
T082-T091 (US4: Export)
  ↓
T092-T106 (Polish)
```

---

## Notes

- **Constitution Compliance**: All tasks follow TDD (tests first), NUMERIC(19,4) for prices, server-side backtest, service layer pattern
- **File Paths**: All backend paths use `snake_case`, frontend paths use `kebab-case` per constitution
- **Language**: Code/variables in English, UI labels in Bahasa Indonesia
- **Checkpoint**: Stop after any phase to validate independent functionality
- **Commit**: Commit after each task or logical group
- **Avoid**: Cross-story dependencies that break independent testability

---

**Total Tasks**: 106  
**Setup**: 7 tasks | **Foundational**: 9 tasks | **US1**: 27 tasks | **US2**: 14 tasks | **US3**: 24 tasks | **US4**: 10 tasks | **Polish**: 15 tasks
