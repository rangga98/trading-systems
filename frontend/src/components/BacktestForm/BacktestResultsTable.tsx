import { Link } from 'react-router-dom'
import type { BacktestResult } from '../../types'

interface BacktestResultsTableProps {
  results: BacktestResult[]
}

export function BacktestResultsTable({ results }: BacktestResultsTableProps) {
  if (results.length === 0) {
    return (
      <div className="p-8 text-center text-muted-foreground border rounded-lg">
        Belum ada hasil backtest
      </div>
    )
  }

  return (
    <div className="overflow-x-auto border rounded-lg">
      <table className="w-full text-sm">
        <thead className="bg-muted">
          <tr>
            <th className="px-4 py-3 text-left font-medium">Status</th>
            <th className="px-4 py-3 text-left font-medium">Total Return</th>
            <th className="px-4 py-3 text-left font-medium">P&L</th>
            <th className="px-4 py-3 text-left font-medium">Win Rate</th>
            <th className="px-4 py-3 text-left font-medium">Trades</th>
            <th className="px-4 py-3 text-left font-medium">Max DD</th>
            <th className="px-4 py-3 text-left font-medium">Sharpe</th>
            <th className="px-4 py-3 text-left font-medium">Aksi</th>
          </tr>
        </thead>
        <tbody>
          {results.map((result) => (
            <tr key={result.id} className="border-t hover:bg-muted/50">
              <td className="px-4 py-3">
                <span
                  className={`px-2 py-1 rounded text-xs ${
                    result.status === 'COMPLETED'
                      ? 'bg-green-100 text-green-800'
                      : result.status === 'FAILED'
                      ? 'bg-red-100 text-red-800'
                      : 'bg-yellow-100 text-yellow-800'
                  }`}
                >
                  {result.status}
                </span>
              </td>
              <td className="px-4 py-3">
                <span
                  className={
                    result.total_return_pct && result.total_return_pct > 0
                      ? 'text-green-600'
                      : result.total_return_pct && result.total_return_pct < 0
                      ? 'text-red-600'
                      : ''
                  }
                >
                  {result.total_return_pct?.toFixed(2) ?? '-'}%
                </span>
              </td>
              <td className="px-4 py-3">
                {result.total_pnl ? `Rp ${Number(result.total_pnl).toLocaleString('id-ID')}` : '-'}
              </td>
              <td className="px-4 py-3">{result.win_rate?.toFixed(1) ?? '-'}%</td>
              <td className="px-4 py-3">{result.total_trades ?? '-'}</td>
              <td className="px-4 py-3 text-red-600">
                {result.max_drawdown_pct ? `${result.max_drawdown_pct.toFixed(2)}%` : '-'}
              </td>
              <td className="px-4 py-3">{result.sharpe_ratio?.toFixed(2) ?? '-'}</td>
              <td className="px-4 py-3">
                <Link
                  to={`/backtest/results/${result.id}`}
                  className="text-primary hover:underline"
                >
                  Detail
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
