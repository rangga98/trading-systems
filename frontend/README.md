# IDX Trading Simulator - Frontend

React 18 + TypeScript frontend for Indonesian Stock Exchange (IDX) trading simulation.

## Architecture

```
src/
├── components/           # Reusable UI components
│   ├── Chart/           # CandlestickChart, TimeframeSelector, EquityCurveChart
│   ├── BacktestForm/    # BacktestConfigForm, ResultsTable, TradeHistoryTable
│   ├── ExportButton.tsx # Export dropdown button
│   └── ImportProgress.tsx # Import job status display
├── pages/               # Route-level page components
│   ├── StockImport/     # StockListPage, StockImportPage, OHLCVViewPage
│   ├── ChartView/       # ChartViewPage
│   └── Backtest/        # BacktestRunPage, ResultsPage, DetailPage
├── services/            # API clients
│   ├── api.ts           # Axios client + TanStack Query setup
│   ├── backtest.ts      # Backtest API functions
│   └── export.ts        # Export download functions
├── types/               # TypeScript type definitions
└── App.tsx              # Main app with routing
```

## Setup

### 1. Environment

```bash
cp .env.example .env.local
# Edit with your backend URL
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Run Development Server

```bash
npm run dev
```

Server runs at `http://localhost:5173`

## Key Components

### Chart Components

**CandlestickChart** (`components/Chart/CandlestickChart.tsx`)
- Interactive candlestick chart using `lightweight-charts`
- Supports zoom, pan, crosshair hover data
- Props: `data`, `onCrosshairMove`

**TimeframeSelector** (`components/Chart/TimeframeSelector.tsx`)
- Daily/Weekly/Monthly toggle buttons
- Props: `value`, `onChange`

**EquityCurveChart** (`components/Chart/EquityCurveChart.tsx`)
- Line chart for backtest equity curve
- Same `lightweight-charts` foundation

### Backtest Components

**BacktestConfigForm** (`components/BacktestForm/BacktestConfigForm.tsx`)
- Form for creating backtest configurations
- Fields: strategy name, ticker, capital, position sizing, SL/TP, date range

**BacktestResultsTable** (`components/BacktestForm/BacktestResultsTable.tsx`)
- Sortable table of backtest results
- Shows: return, P&L, win rate, trades, max drawdown, Sharpe ratio

**TradeHistoryTable** (`components/BacktestForm/TradeHistoryTable.tsx`)
- Detailed trade list with entry/exit prices, P&L, exit reasons

**ExportButton** (`components/ExportButton.tsx`)
- Dropdown button for CSV/JSON export
- Auto-generates filename with ticker and date range

### Data Fetching

All data fetching uses **TanStack Query** with the following caching strategy:
- Stock lists: 5 minutes stale time
- OHLCV data: 10 minutes stale time
- Backtest configs: 1 minute stale time
- Backtest results: 30 seconds stale time

API client in `services/api.ts` handles:
- Base URL configuration via `VITE_API_URL`
- Request/response interceptors
- Error logging

## Pages & Routes

| Route | Page | Description |
|-------|------|-------------|
| `/` | Dashboard | Welcome page |
| `/stocks` | StockListPage | View all stocks, search, delete |
| `/stocks/import` | StockImportPage | Import OHLCV from yfinance |
| `/stocks/:ticker` | OHLCVViewPage | View raw OHLCV data table |
| `/chart` | ChartViewPage | Interactive candlestick chart |
| `/backtest/run` | BacktestRunPage | Create backtest configuration |
| `/backtest/results` | BacktestResultsPage | List configs and results |
| `/backtest/results/:resultId` | BacktestDetailPage | View metrics, equity curve, trades |

## Styling

Uses **Tailwind CSS** with custom theme variables:
- `bg-background` - App background
- `bg-card` - Card/panel background
- `text-primary` / `bg-primary` - Primary actions
- `text-muted-foreground` - Secondary text

## Error Handling

- **Global Error Boundary**: Catches React render errors, shows user-friendly message
- **API Errors**: Handled by TanStack Query + response interceptors
- **404**: Fallback UI for unknown routes
