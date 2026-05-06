import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { BacktestResultsTable } from '../../components/BacktestForm'
import { backtestApi } from '../../services/backtest'

export function BacktestResultsPage() {
  const [page, setPage] = useState(0)
  const limit = 20

  const { data: configsData, isLoading: configsLoading } = useQuery({
    queryKey: ['backtest-configs'],
    queryFn: () => backtestApi.getConfigs(50, 0),
  })

  const { data: resultsData, isLoading: resultsLoading, refetch } = useQuery({
    queryKey: ['backtest-results', page],
    queryFn: () => backtestApi.getResults(undefined, limit, page * limit),
  })

  const executeMutation = useMutation({
    mutationFn: (configId: string) => backtestApi.execute(configId),
    onSuccess: () => {
      refetch()
    },
  })

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Backtest - Hasil</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Lihat hasil backtest dan bandingkan performa strategi
          </p>
        </div>
        <div className="flex gap-2">
          <Link
            to="/backtest/run"
            className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
          >
            + Konfigurasi Baru
          </Link>
        </div>
      </div>

      {/* Configs */}
      <div className="space-y-2">
        <h2 className="text-lg font-semibold">Konfigurasi Tersedia</h2>
        {configsLoading ? (
          <div className="animate-pulse h-20 bg-muted rounded-lg" />
        ) : configsData && configsData.items.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {configsData.items.map((config) => (
              <div key={config.id} className="p-4 border rounded-lg bg-card">
                <h3 className="font-medium">{config.name}</h3>
                <p className="text-sm text-muted-foreground mt-1">
                  {config.ticker} • Rp {Number(config.initial_capital).toLocaleString('id-ID')}
                </p>
                <p className="text-sm text-muted-foreground">
                  {config.date_range_start} - {config.date_range_end}
                </p>
                <div className="mt-3 flex gap-2">
                  <button
                    onClick={() => executeMutation.mutate(config.id)}
                    disabled={executeMutation.isPending}
                    className="px-3 py-1.5 text-sm bg-primary text-primary-foreground rounded hover:bg-primary/90 disabled:opacity-50"
                  >
                    Jalankan
                  </button>
                  <Link
                    to={`/backtest/results?config_id=${config.id}`}
                    className="px-3 py-1.5 text-sm border rounded hover:bg-muted"
                  >
                    Lihat Hasil
                  </Link>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-muted-foreground">
            Belum ada konfigurasi.{' '}
            <Link to="/backtest/run" className="text-primary hover:underline">
              Buat konfigurasi baru
            </Link>
          </p>
        )}
      </div>

      {/* Results Table */}
      <div className="space-y-2">
        <h2 className="text-lg font-semibold">Riwayat Hasil Backtest</h2>
        {resultsLoading ? (
          <div className="animate-pulse h-40 bg-muted rounded-lg" />
        ) : (
          <>
            <BacktestResultsTable results={resultsData?.items || []} />
            
            {resultsData && resultsData.total > limit && (
              <div className="flex justify-between items-center mt-4">
                <button
                  onClick={() => setPage(p => Math.max(0, p - 1))}
                  disabled={page === 0}
                  className="px-3 py-1 border rounded hover:bg-muted disabled:opacity-50"
                >
                  Sebelumnya
                </button>
                <span className="text-sm text-muted-foreground">
                  Halaman {page + 1} dari {Math.ceil(resultsData.total / limit)}
                </span>
                <button
                  onClick={() => setPage(p => p + 1)}
                  disabled={(page + 1) * limit >= resultsData.total}
                  className="px-3 py-1 border rounded hover:bg-muted disabled:opacity-50"
                >
                  Selanjutnya
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
