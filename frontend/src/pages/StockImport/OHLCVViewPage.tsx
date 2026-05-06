import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { ohlcvApi } from '../../services/ohlcv'
import { DataTable } from '../../components/DataTable'
import type { OHLCVData } from '../../types'

export function OHLCVViewPage() {
  const { ticker } = useParams<{ ticker: string }>()

  const { data, isLoading, error } = useQuery({
    queryKey: ['ohlcv', ticker],
    queryFn: () => ohlcvApi.getData(ticker!, { limit: 100 }),
    enabled: !!ticker,
  })

  const columns = [
    { key: 'date', header: 'Tanggal' },
    { key: 'open', header: 'Open' },
    { key: 'high', header: 'High' },
    { key: 'low', header: 'Low' },
    { key: 'close', header: 'Close' },
    { key: 'adj_close', header: 'Adj Close' },
    {
      key: 'volume',
      header: 'Volume',
      render: (item: OHLCVData) => Number(item.volume).toLocaleString('id-ID'),
    },
  ]

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Data OHLCV: {ticker}</h1>
          <p className="text-muted-foreground">
            {data?.count || 0} data historis ditemukan
          </p>
        </div>
        <div className="flex gap-2">
          <Link
            to={`/chart?ticker=${ticker}`}
            className="px-4 py-2 bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/90"
          >
            Lihat Grafik
          </Link>
          <Link
            to="/stocks"
            className="px-4 py-2 border rounded-md hover:bg-muted"
          >
            Kembali
          </Link>
        </div>
      </div>

      {isLoading && <p>Memuat data...</p>}
      {error && <p className="text-red-600">Error: {error.message}</p>}

      {data && (
        <DataTable
          data={data.data}
          columns={columns}
          keyExtractor={(item) => `${ticker}-${item.date}`}
          emptyMessage="Belum ada data untuk saham ini"
        />
      )}
    </div>
  )
}
