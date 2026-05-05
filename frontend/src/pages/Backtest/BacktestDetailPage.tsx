import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { EquityCurveChart } from '../../components/Chart'
import { TradeHistoryTable } from '../../components/BacktestForm'
import { backtestApi } from '../../services/backtest'

export function BacktestDetailPage() {
  const { resultId } = useParams<{ resultId: string }>()

  const { data: result, isLoading } = useQuery({
    queryKey: ['backtest-result', resultId],
    queryFn: () => backtestApi.getResult(resultId!),
    enabled: !!resultId,
  })

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="animate-pulse h-8 w-64 bg-muted rounded" />
        <div className="animate-pulse h-40 bg-muted rounded-lg" />
        <div className="animate-pulse h-40 bg-muted rounded-lg" />
      </div>
    )
  }

  if (!result) {
    return (
      <div className="p-8 text-center text-muted-foreground">
        Hasil backtest tidak ditemukan
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Detail Hasil Backtest</h1>
        <p className="text-sm text-muted-foreground mt-1">
          ID: {result.id}
        </p>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="p-4 border rounded-lg bg-card">
          <p className="text-sm text-muted-foreground">Total Return</p>
          <p className={`text-2xl font-bold ${
            result.total_return_pct && result.total_return_pct > 0
              ? 'text-green-600'
              : result.total_return_pct && result.total_return_pct < 0
              ? 'text-red-600'
              : ''
          }`}>
            {result.total_return_pct?.toFixed(2) ?? '-'}%
          </p>
        </div>
        <div className="p-4 border rounded-lg bg-card">
          <p className="text-sm text-muted-foreground">P&L Total</p>
          <p className="text-2xl font-bold">
            {result.total_pnl
              ? `Rp ${Number(result.total_pnl).toLocaleString('id-ID')}`
              : '-'}
          </p>
        </div>
        <div className="p-4 border rounded-lg bg-card">
          <p className="text-sm text-muted-foreground">Win Rate</p>
          <p className="text-2xl font-bold">
            {result.win_rate?.toFixed(1) ?? '-'}%
          </p>
        </div>
        <div className="p-4 border rounded-lg bg-card">
          <p className="text-sm text-muted-foreground">Max Drawdown</p>
          <p className="text-2xl font-bold text-red-600">
            {result.max_drawdown_pct ? `${result.max_drawdown_pct.toFixed(2)}%` : '-'}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="p-4 border rounded-lg bg-card">
          <p className="text-sm text-muted-foreground">Sharpe Ratio</p>
          <p className="text-2xl font-bold">
            {result.sharpe_ratio?.toFixed(2) ?? '-'}
          </p>
        </div>
        <div className="p-4 border rounded-lg bg-card">
          <p className="text-sm text-muted-foreground">Total Trades</p>
          <p className="text-2xl font-bold">
            {result.total_trades ?? '-'}
          </p>
        </div>
      </div>

      {/* Equity Curve Chart */}
      {result.equity_curve && result.equity_curve.length > 0 && (
        <div className="space-y-2">
          <h2 className="text-lg font-semibold">Equity Curve</h2>
          <div className="h-[300px] border rounded-lg">
            <EquityCurveChart data={result.equity_curve} />
          </div>
        </div>
      )}

      {/* Trade History */}
      {result.trades && result.trades.length > 0 && (
        <div className="space-y-2">
          <h2 className="text-lg font-semibold">Riwayat Transaksi</h2>
          <TradeHistoryTable trades={result.trades} />
        </div>
      )}

      {/* Status */}
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <span
          className={`w-2 h-2 rounded-full ${
            result.status === 'COMPLETED'
              ? 'bg-green-500'
              : result.status === 'FAILED'
              ? 'bg-red-500'
              : 'bg-yellow-500'
          }`}
        />
        Status: {result.status}
      </div>
    </div>
  )
}
