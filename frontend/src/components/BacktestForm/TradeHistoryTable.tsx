import type { Trade } from '../../types'

interface TradeHistoryTableProps {
  trades: Trade[]
}

export function TradeHistoryTable({ trades }: TradeHistoryTableProps) {
  if (trades.length === 0) {
    return (
      <div className="p-8 text-center text-muted-foreground border rounded-lg">
        Tidak ada transaksi
      </div>
    )
  }

  return (
    <div className="overflow-x-auto border rounded-lg">
      <table className="w-full text-sm">
        <thead className="bg-muted">
          <tr>
            <th className="px-4 py-3 text-left font-medium">Entry Date</th>
            <th className="px-4 py-3 text-left font-medium">Exit Date</th>
            <th className="px-4 py-3 text-right font-medium">Entry Price</th>
            <th className="px-4 py-3 text-right font-medium">Exit Price</th>
            <th className="px-4 py-3 text-right font-medium">Position Size</th>
            <th className="px-4 py-3 text-right font-medium">P&L</th>
            <th className="px-4 py-3 text-right font-medium">P&L %</th>
            <th className="px-4 py-3 text-left font-medium">Exit Reason</th>
          </tr>
        </thead>
        <tbody>
          {trades.map((trade) => (
            <tr key={trade.id} className="border-t hover:bg-muted/50">
              <td className="px-4 py-3">{trade.entry_date}</td>
              <td className="px-4 py-3">{trade.exit_date || '-'}</td>
              <td className="px-4 py-3 text-right">
                {Number(trade.entry_price).toLocaleString('id-ID')}
              </td>
              <td className="px-4 py-3 text-right">
                {trade.exit_price ? Number(trade.exit_price).toLocaleString('id-ID') : '-'}
              </td>
              <td className="px-4 py-3 text-right">
                {trade.position_size.toLocaleString('id-ID')}
              </td>
              <td
                className={`px-4 py-3 text-right ${
                  trade.pnl
                        ? Number(trade.pnl) > 0
                          ? 'text-green-600'
                          : 'text-red-600'
                        : ''
                }`}
              >
                {trade.pnl
                  ? `Rp ${Number(trade.pnl).toLocaleString('id-ID')}`
                  : '-'}
              </td>
              <td
                className={`px-4 py-3 text-right ${
                  trade.pnl_pct && trade.pnl_pct > 0
                    ? 'text-green-600'
                    : trade.pnl_pct && trade.pnl_pct < 0
                    ? 'text-red-600'
                    : ''
                }`}
              >
                {trade.pnl_pct !== undefined ? `${trade.pnl_pct.toFixed(2)}%` : '-'}
              </td>
              <td className="px-4 py-3">
                <span className="px-2 py-1 rounded text-xs bg-muted">
                  {trade.exit_reason || 'OPEN'}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
