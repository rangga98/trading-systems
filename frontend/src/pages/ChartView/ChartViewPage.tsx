import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { CandlestickChart, TimeframeSelector } from '../../components/Chart'
import { ohlcvApi } from '../../services/ohlcv'
import { stocksApi } from '../../services/stocks'
import type { OHLCVData } from '../../types'

export function ChartViewPage() {
  const [selectedTicker, setSelectedTicker] = useState('')
  const [timeframe, setTimeframe] = useState<'daily' | 'weekly' | 'monthly'>('daily')
  const [hoverData, setHoverData] = useState<OHLCVData | null>(null)

  // Fetch stock list for dropdown
  const { data: stocksData, isLoading: stocksLoading } = useQuery({
    queryKey: ['stocks', 'has-data'],
    queryFn: () => stocksApi.getAll(undefined, true, 100, 0),
  })

  // Fetch OHLCV data
  const { data: ohlcvData, isLoading: ohlcvLoading, error } = useQuery({
    queryKey: ['ohlcv', selectedTicker, timeframe],
    queryFn: () =>
      selectedTicker
        ? ohlcvApi.getData(selectedTicker, { timeframe, limit: 1000 })
        : null,
    enabled: !!selectedTicker,
  })

  const handleCrosshairMove = (data: OHLCVData | null) => {
    setHoverData(data)
  }

  return (
    <div className="h-full flex flex-col gap-4">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Grafik Candlestick</h1>
          <p className="text-sm text-muted-foreground">
            Visualisasi data historis dengan zoom dan pan
          </p>
        </div>

        <div className="flex items-center gap-4">
          {/* Ticker Selector */}
          <select
            value={selectedTicker}
            onChange={(e) => setSelectedTicker(e.target.value)}
            className="px-3 py-2 border rounded-md min-w-[200px]"
            disabled={stocksLoading}
          >
            <option value="">Pilih Saham...</option>
            {stocksData?.items.map((stock) => (
              <option key={stock.id} value={stock.ticker}>
                {stock.ticker} - {stock.name}
              </option>
            ))}
          </select>

          {/* Timeframe Selector */}
          <TimeframeSelector
            value={timeframe}
            onChange={setTimeframe}
            disabled={!selectedTicker || ohlcvLoading}
          />
        </div>
      </div>

      {/* Hover Data Display */}
      {hoverData && (
        <div className="flex gap-6 p-3 bg-muted rounded-lg text-sm">
          <div>
            <span className="text-muted-foreground">Tanggal:</span>{' '}
            <span className="font-medium">{hoverData.date}</span>
          </div>
          <div>
            <span className="text-muted-foreground">Open:</span>{' '}
            <span className="font-medium">{hoverData.open}</span>
          </div>
          <div>
            <span className="text-muted-foreground">High:</span>{' '}
            <span className="font-medium">{hoverData.high}</span>
          </div>
          <div>
            <span className="text-muted-foreground">Low:</span>{' '}
            <span className="font-medium">{hoverData.low}</span>
          </div>
          <div>
            <span className="text-muted-foreground">Close:</span>{' '}
            <span className="font-medium">{hoverData.close}</span>
          </div>
          <div>
            <span className="text-muted-foreground">Volume:</span>{' '}
            <span className="font-medium">
              {Number(hoverData.volume).toLocaleString('id-ID')}
            </span>
          </div>
        </div>
      )}

      {/* Chart Container */}
      <div className="flex-1 min-h-[500px] border rounded-lg bg-card relative">
        {!selectedTicker ? (
          <div className="absolute inset-0 flex items-center justify-center text-muted-foreground">
            <div className="text-center">
              <p className="text-lg mb-2">Pilih saham untuk melihat grafik</p>
              <p className="text-sm">
                Saham harus memiliki data yang sudah diimpor
              </p>
            </div>
          </div>
        ) : ohlcvLoading ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4" />
              <p className="text-muted-foreground">Memuat data...</p>
            </div>
          </div>
        ) : error ? (
          <div className="absolute inset-0 flex items-center justify-center text-red-600">
            <div className="text-center">
              <p className="text-lg mb-2">Error memuat data</p>
              <p className="text-sm">{(error as Error).message}</p>
            </div>
          </div>
        ) : ohlcvData && ohlcvData.data.length === 0 ? (
          <div className="absolute inset-0 flex items-center justify-center text-muted-foreground">
            <div className="text-center">
              <p className="text-lg mb-2">Tidak ada data</p>
              <p className="text-sm">
                Impor data untuk {selectedTicker} terlebih dahulu
              </p>
            </div>
          </div>
        ) : ohlcvData ? (
          <CandlestickChart
            data={ohlcvData.data}
            onCrosshairMove={handleCrosshairMove}
            className="rounded-lg"
          />
        ) : null}
      </div>

      {/* Chart Info */}
      {ohlcvData && (
        <div className="flex justify-between items-center text-sm text-muted-foreground">
          <span>
            {ohlcvData.ticker} • {ohlcvData.timeframe} • {ohlcvData.count} data
          </span>
          <span>
            Gunakan scroll untuk zoom, drag untuk pan
          </span>
        </div>
      )}
    </div>
  )
}
