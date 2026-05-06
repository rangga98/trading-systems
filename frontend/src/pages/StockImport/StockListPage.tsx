import { useQuery } from '@tanstack/react-query'
import { useState, useMemo } from 'react'
import { Link } from 'react-router-dom'
import { stocksApi } from '../../services/stocks'
import { DataTable } from '../../components/DataTable'
import { StockExportButton } from '../../components/StockExportButton'
import type { Stock } from '../../types'

export function StockListPage() {
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(0)
  const [selectedStocksMap, setSelectedStocksMap] = useState<Map<string, Stock>>(new Map())
  const limit = 20

  const { data, isLoading, error } = useQuery({
    queryKey: ['stocks', search, page],
    queryFn: () => stocksApi.getAll(search, undefined, limit, page * limit),
  })

  const selectedIds = useMemo(() => new Set(selectedStocksMap.keys()), [selectedStocksMap])
  const selectedStocks = useMemo(() => Array.from(selectedStocksMap.values()), [selectedStocksMap])

  const handleSelectionChange = (newSelectedIds: Set<string>) => {
    const nextMap = new Map(selectedStocksMap)
    
    // Items on current page
    const currentItems = data?.items || []
    
    // For each item on current page, update its presence in the map
    currentItems.forEach(item => {
      if (newSelectedIds.has(item.id)) {
        nextMap.set(item.id, item)
      } else {
        nextMap.delete(item.id)
      }
    })
    
    setSelectedStocksMap(nextMap)
  }

  const columns = [
    {
      key: 'ticker',
      header: 'Kode',
      render: (stock: Stock) => (
        <Link
          to={`/stocks/${stock.ticker}`}
          className="font-medium text-primary hover:underline"
        >
          {stock.ticker}
        </Link>
      ),
    },
    { key: 'name', header: 'Nama Perusahaan' },
    { key: 'sector', header: 'Sektor' },
    {
      key: 'has_data',
      header: 'Data',
      render: (stock: Stock) => (
        <span
          className={`px-2 py-1 rounded text-xs ${
            stock.has_data
              ? 'bg-green-100 text-green-800'
              : 'bg-gray-100 text-gray-800'
          }`}
        >
          {stock.has_data ? `${stock.data_count} data` : 'Belum ada'}
        </span>
      ),
    },
    {
      key: 'date_range',
      header: 'Rentang Tanggal',
      render: (stock: Stock) =>
        stock.date_range
          ? `${stock.date_range.start} s/d ${stock.date_range.end}`
          : '-',
    },
  ]

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Daftar Saham</h1>
        <div className="flex gap-2">
          <StockExportButton selectedStocks={selectedStocks} />
          <Link
            to="/stocks/import"
            className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
          >
            + Impor Saham Baru
          </Link>
        </div>
      </div>

      <div className="flex gap-2">
        <input
          type="text"
          placeholder="Cari kode atau nama..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="px-3 py-2 border rounded-md max-w-sm"
        />
      </div>

      {isLoading && <p>Memuat data...</p>}
      {error && <p className="text-red-600">Error: {error.message}</p>}

      {data && (
        <>
          <DataTable
            data={data.items}
            columns={columns}
            keyExtractor={(stock) => stock.id}
            emptyMessage="Tidak ada saham ditemukan"
            selectable
            selectedIds={selectedIds}
            onSelectionChange={handleSelectionChange}
          />

          <div className="flex justify-between items-center pt-4">
            <p className="text-sm text-muted-foreground">
              Menampilkan {data.items.length} dari {data.total} saham
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => setPage((p) => Math.max(0, p - 1))}
                disabled={page === 0}
                className="px-3 py-1 border rounded disabled:opacity-50"
              >
                Sebelumnya
              </button>
              <button
                onClick={() => setPage((p) => p + 1)}
                disabled={(page + 1) * limit >= data.total}
                className="px-3 py-1 border rounded disabled:opacity-50"
              >
                Berikutnya
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
