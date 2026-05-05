import { useState } from 'react'
import { ohlcvApi } from '../services/ohlcv'
import { useAppStore } from '../stores/appStore'

interface StockImportFormProps {
  onSuccess?: () => void
}

export function StockImportForm({ onSuccess }: StockImportFormProps) {
  const [ticker, setTicker] = useState('')
  const [startDate, setStartDate] = useState('2020-01-01')
  const [endDate, setEndDate] = useState(new Date().toISOString().split('T')[0])
  const [onConflict, setOnConflict] = useState<'skip' | 'overwrite' | 'merge'>('skip')
  const [isLoading, setIsLoading] = useState(false)
  
  const { addNotification } = useAppStore()

  const validateTicker = (value: string): boolean => {
    // IDX ticker must end with .JK
    return /^[A-Z0-9]+\.JK$/i.test(value)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateTicker(ticker)) {
      addNotification({
        type: 'error',
        message: 'Format ticker tidak valid. Harus diakhiri dengan .JK (contoh: BBCA.JK)',
        duration: 5000,
      })
      return
    }

    setIsLoading(true)
    
    try {
      const result = await ohlcvApi.importData(ticker.toUpperCase(), {
        start_date: startDate,
        end_date: endDate,
        on_conflict: onConflict,
      })
      
      addNotification({
        type: 'success',
        message: `Impor berhasil! ${result.records_imported} data diimpor, ${result.records_skipped} dilewati, ${result.records_updated} diperbarui.`,
        duration: 5000,
      })
      
      onSuccess?.()
    } catch (error: any) {
      addNotification({
        type: 'error',
        message: error.response?.data?.detail || 'Gagal mengimpor data',
        duration: 5000,
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 p-4 border rounded-lg bg-card">
      <h2 className="text-lg font-semibold">Impor Data Saham</h2>
      
      <div>
        <label htmlFor="ticker" className="block text-sm font-medium mb-1">
          Kode Saham (Ticker)
        </label>
        <input
          id="ticker"
          type="text"
          value={ticker}
          onChange={(e) => setTicker(e.target.value.toUpperCase())}
          placeholder="Contoh: BBCA.JK"
          className="w-full px-3 py-2 border rounded-md"
          required
        />
        <p className="text-sm text-muted-foreground mt-1">
          Format: KODE.JK (contoh: BBCA.JK, BBRI.JK)
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label htmlFor="startDate" className="block text-sm font-medium mb-1">
            Tanggal Mulai
          </label>
          <input
            id="startDate"
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            className="w-full px-3 py-2 border rounded-md"
            required
          />
        </div>
        
        <div>
          <label htmlFor="endDate" className="block text-sm font-medium mb-1">
            Tanggal Akhir
          </label>
          <input
            id="endDate"
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            className="w-full px-3 py-2 border rounded-md"
            required
          />
        </div>
      </div>

      <div>
        <label htmlFor="onConflict" className="block text-sm font-medium mb-1">
          Jika Data Sudah Ada
        </label>
        <select
          id="onConflict"
          value={onConflict}
          onChange={(e) => setOnConflict(e.target.value as any)}
          className="w-full px-3 py-2 border rounded-md"
        >
          <option value="skip">Lewati (skip)</option>
          <option value="overwrite">Timpa semua (overwrite)</option>
          <option value="merge">Perbarui jika berbeda (merge)</option>
        </select>
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50"
      >
        {isLoading ? 'Mengimpor...' : 'Impor Data'}
      </button>
    </form>
  )
}
