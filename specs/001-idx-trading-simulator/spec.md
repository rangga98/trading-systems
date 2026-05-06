# Feature Specification: IDX Trading Simulation Web App

**Feature Branch**: `001-idx-trading-simulator`  
**Created**: 2026-05-04  
**Status**: Draft  
**Input**: User description: "I want to build a trading simulation web app for Indonesian stock market (IDX). The app allows users to import historical OHLCV data (date, open, high, low, close, adj close, volume) for IDX tickers like BBCA, BBRI, etc. using yfinance, store it in PostgreSQL, and visualize it as an interactive candlestick chart. The core feature is a backtesting engine where users can test trading strategies against historical data, manage money (initial capital, position sizing, risk per trade, stop loss, take profit), and see results including P&L, equity curve, win rate, and max drawdown. Future features include technical indicators (MA, RSI, MACD, Bollinger Bands) and rule-based strategy builder. Tech stack: Python FastAPI backend, React frontend, PostgreSQL database."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Import Historical Stock Data (Priority: P1)

As a trader, I want to import historical OHLCV data for IDX tickers (BBCA, BBRI, etc.) so I can analyze and test strategies against real market data.

**Why this priority**: Without historical data, no backtesting or analysis is possible. This is the foundational requirement for the entire application.

**Independent Test**: Can be tested by entering a ticker symbol (e.g., BBCA.JK) and date range, then verifying the data appears in the database and can be viewed in a table format.

**Acceptance Scenarios**:

1. **Given** a user enters a valid IDX ticker (e.g., "BBCA.JK") and date range, **When** they initiate import, **Then** the system fetches OHLCV data via yfinance and stores it in PostgreSQL with progress feedback.
2. **Given** data already exists for a ticker/date range, **When** user attempts re-import, **Then** the system offers to skip, overwrite, or merge duplicate records.
3. **Given** an invalid or non-existent ticker, **When** import is attempted, **Then** the system displays a clear error message without crashing.

---

### User Story 2 - Visualize Candlestick Charts (Priority: P1)

As a trader, I want to view interactive candlestick charts of imported data so I can visually analyze price movements and patterns.

**Why this priority**: Visual analysis is essential for traders to understand market behavior; without visualization, the raw data is difficult to interpret.

**Independent Test**: Can be tested by selecting an imported ticker and verifying an interactive candlestick chart renders with zoom, pan, and timeframe selection capabilities.

**Acceptance Scenarios**:

1. **Given** imported data exists for a ticker, **When** user selects it from a dropdown, **Then** an interactive candlestick chart displays with date range on x-axis and price on y-axis.
2. **Given** a rendered chart, **When** user zooms or pans, **Then** the chart updates smoothly without page reload.
3. **Given** a chart view, **When** user switches timeframe (daily/weekly/monthly), **Then** candlesticks aggregate accordingly and the view updates.

---

### User Story 3 - Execute Backtesting with Money Management (Priority: P1)

As a trader, I want to run backtests with configurable money management parameters (initial capital, position sizing, stop loss, take profit) so I can evaluate strategy profitability and risk.

**Why this priority**: Backtesting with money management is the core value proposition - it allows traders to validate strategies before risking real capital.

**Independent Test**: Can be tested by configuring a simple buy-and-hold strategy with Rp 100.000.000 initial capital and verifying the system generates P&L, equity curve, and performance metrics.

**Acceptance Scenarios**:

1. **Given** imported historical data exists, **When** user configures a strategy with initial capital (Rp 100.000.000), position sizing (e.g., 10% per trade), stop loss (5%), and take profit (10%), **Then** the backtest executes and produces trade history.
2. **Given** a completed backtest, **When** results are displayed, **Then** user sees P&L, equity curve chart, win rate, total trades, and max drawdown.
3. **Given** multiple strategies configured, **When** backtests complete, **Then** results are comparable side-by-side with sortable metrics.

---

### User Story 4 - Export Backtest Results (Priority: P2)

As a trader, I want to export backtest results and trade history to CSV so I can perform external analysis or keep records.

**Why this priority**: Useful for power users but not essential for basic backtesting functionality.

**Independent Test**: Can be tested by clicking "Export" on a backtest result and verifying the CSV contains all trades with timestamps, prices, P&L.

**Acceptance Scenarios**:

1. **Given** a completed backtest, **When** user clicks "Export Results", **Then** a CSV file downloads containing all trade details.
2. **Given** the exported CSV, **When** opened in Excel/sheet software, **Then** all columns are properly formatted and readable.

---

### Edge Cases

- **Empty data import**: What happens when yfinance returns no data for a valid ticker/date range? → System should display "No data available" message.
- **Concurrent backtests**: How does the system handle multiple simultaneous backtest requests? → Queue or process sequentially with progress indicators.
- **Invalid money management parameters**: What if user sets stop loss > take profit, or negative capital? → Validate inputs and reject with clear error messages.
- **Data gaps**: How are missing trading days (holidays, weekends) handled in backtesting? → System should skip non-trading days without breaking calculations.
- **Large dataset performance**: What happens with 10+ years of daily data? → System should paginate or use virtualized rendering to maintain responsiveness.
- **Database connection failure**: How does the system behave if PostgreSQL is unavailable? → Display connection error and offer retry option.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow users to import historical OHLCV data for IDX tickers using yfinance API with date range selection.
- **FR-002**: System MUST store imported stock data in PostgreSQL with proper indexing on ticker symbol and date columns.
- **FR-003**: System MUST display interactive candlestick charts with zoom, pan, and timeframe selection capabilities.
- **FR-004**: System MUST provide a backtesting engine that simulates trades against historical data with configurable entry/exit rules.
- **FR-005**: System MUST support money management parameters: initial capital, position sizing (fixed amount, percentage, or risk-based), stop loss, and take profit.
- **FR-006**: System MUST calculate and display backtest performance metrics: total P&L, equity curve, win rate, total trades, max drawdown, and Sharpe ratio.
- **FR-007**: System MUST allow users to create and save multiple backtest configurations for comparison.
- **FR-008**: System MUST use WIB (UTC+7) timezone for all date/time handling and display.
- **FR-009**: System MUST handle data import conflicts (duplicate records) with user-selectable options: skip, overwrite, or merge.
- **FR-010**: System MUST validate all user inputs (ticker symbols, date ranges, money management parameters) and provide clear error messages.
- **FR-011**: System MUST export backtest results and trade history to CSV format.
- **FR-012**: System MUST handle IDX-specific market conventions: .JK suffix for tickers, WIB timezone, and Jakarta Stock Exchange holidays.

### Key Entities *(include if feature involves data)*

- **Stock**: Represents an IDX-listed company with ticker symbol (e.g., BBCA.JK), company name, and sector. Tracks metadata about the tradable instrument.
- **OHLCV Data**: Historical price data containing date, open price, high price, low price, close price, adjusted close price, and volume. Linked to a Stock by ticker symbol. Time-series data with daily/weekly/monthly granularity.
- **Backtest Configuration**: User-defined trading strategy parameters including entry rules, exit rules, initial capital, position sizing method, stop loss percentage, take profit percentage, and date range. Belongs to a User.
- **Trade**: Individual simulated trade generated during backtesting with entry date, entry price, exit date, exit price, position size, P&L, and status (open/closed). Linked to a Backtest Run.
- **Backtest Result**: Summary of a backtest execution including total P&L, equity curve data points, win rate, total trades, max drawdown, Sharpe ratio, and execution timestamp. Linked to a Backtest Configuration.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can import 5 years of daily OHLCV data for a ticker in under 30 seconds with progress indication.
- **SC-002**: Candlestick charts render with less than 2 seconds load time for 1000 data points and support smooth zoom/pan interactions.
- **SC-003**: Backtest engine processes 5 years of daily data (approximately 1250 bars) in under 5 seconds.
- **SC-004**: 90% of users successfully complete their first backtest without requiring support or documentation.
- **SC-005**: System correctly handles all 600+ IDX-listed stocks available through yfinance.
- **SC-006**: Backtest results accuracy: simulated P&L calculations match expected values within 0.01% margin of error.
- **SC-007**: Application supports concurrent usage by at least 10 users without performance degradation.
- **SC-008**: Data import achieves 99.9% success rate for valid ticker/date range combinations.

## Assumptions

- Users have basic understanding of stock trading concepts (OHLCV, P&L, stop loss, take profit).
- yfinance library maintains reliable access to Yahoo Finance data for IDX tickers.
- PostgreSQL database will be hosted and accessible with appropriate connection credentials.
- Single-user deployment is acceptable for initial version; multi-user support can be added later.
- Jakarta/Indonesia timezone (WIB, UTC+7) is used for all date/time handling.
- IDX market holidays are handled by the data source (yfinance); no custom holiday calendar implementation required for MVP.
- Modern web browser with JavaScript enabled is required (Chrome, Firefox, Safari, Edge).
- Initial data import will be limited to daily granularity; intraday data is out of scope for v1.
- Frontend and backend will be deployed together on a single server for initial version.
- No real-time data streaming required; all data is historical batch imports.

## Future Considerations (Out of Scope)

- User Authentication: Login, sessions, per-user data isolation
- Watchlist: Personal ticker watchlist with quick dashboard access

- **Technical Indicators**: Moving averages (SMA, EMA), RSI, MACD, Bollinger Bands for strategy building.
- **Rule-Based Strategy Builder**: Visual drag-and-drop interface for creating complex trading strategies without coding.
- **Real-time Data**: Live price streaming and alerts.
- **Multi-User Collaboration**: Sharing backtests and strategies between users.
- **Advanced Analytics**: Monte Carlo simulation, walk-forward analysis, optimization of strategy parameters.
- **Mobile Application**: Native iOS/Android apps.
- **Paper Trading**: Simulated trading with live market data but no real money.
