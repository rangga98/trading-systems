// Stock types
export interface Stock {
  id: string
  ticker: string
  name: string
  sector?: string
  has_data: boolean
  data_count: number
  date_range?: {
    start: string
    end: string
  }
  created_at: string
  updated_at: string
}

export interface StockCreateRequest {
  ticker: string
}

export interface StockListResponse {
  items: Stock[]
  total: number
  limit: number
  offset: number
}

// OHLCV types
export interface OHLCVData {
  date: string
  open: string
  high: string
  low: string
  close: string
  adj_close: string
  volume: number
}

export interface OHLCVResponse {
  ticker: string
  timeframe: 'daily' | 'weekly' | 'monthly'
  count: number
  data: OHLCVData[]
}

export interface OHLCVImportRequest {
  start_date: string
  end_date: string
  on_conflict?: 'skip' | 'overwrite' | 'merge'
}

export interface ImportJob {
  job_id: string
  ticker: string
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED'
  start_date: string
  end_date: string
  records_imported?: number
  records_total?: number
  total_records?: number
  progress?: number
  error_message?: string
  created_at: string
  updated_at: string
}

// Backtest types
export interface BacktestConfig {
  id: string
  name: string
  ticker: string
  initial_capital: string
  position_sizing_type: 'FIXED_AMOUNT' | 'FIXED_PCT' | 'RISK_BASED'
  position_size_value: string
  stop_loss_pct?: number
  take_profit_pct?: number
  entry_rules: object
  exit_rules: object
  date_range_start: string
  date_range_end: string
  created_at: string
  updated_at: string
}

export interface BacktestConfigCreateRequest {
  name: string
  ticker: string
  initial_capital: number
  position_sizing_type: 'FIXED_AMOUNT' | 'FIXED_PCT' | 'RISK_BASED'
  position_size_value: number
  stop_loss_pct?: number
  take_profit_pct?: number
  entry_rules?: object
  exit_rules?: object
  date_range_start: string
  date_range_end: string
}

export interface Trade {
  id: string
  entry_date: string
  entry_price: string
  exit_date?: string
  exit_price?: string
  position_size: number
  position_type: 'LONG' | 'SHORT'
  pnl?: string
  pnl_pct?: number
  exit_reason?: 'STOP_LOSS' | 'TAKE_PROFIT' | 'END_OF_DATA' | 'SIGNAL'
}

export interface BacktestResult {
  id: string
  config_id: string
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED'
  total_pnl?: string
  total_return_pct?: number
  win_rate?: number
  total_trades?: number
  max_drawdown?: string
  max_drawdown_pct?: number
  sharpe_ratio?: number
  equity_curve?: { date: string; equity: string }[]
  executed_at: string
  completed_at?: string
  error_message?: string
}

export interface BacktestDetailResponse {
  result: BacktestResult
  trades: Trade[]
  config: BacktestConfig
}

// Common types
export interface ApiError {
  detail: string
  status_code: number
}
