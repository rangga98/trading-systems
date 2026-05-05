import { useState } from 'react'
import type { BacktestConfigCreateRequest } from '../../types'

interface BacktestConfigFormProps {
  onSubmit: (data: BacktestConfigCreateRequest) => void
  isLoading?: boolean
  initialData?: Partial<BacktestConfigCreateRequest>
}

export function BacktestConfigForm({ onSubmit, isLoading, initialData }: BacktestConfigFormProps) {
  const [formData, setFormData] = useState<BacktestConfigCreateRequest>({
    name: initialData?.name || '',
    ticker: initialData?.ticker || '',
    initial_capital: initialData?.initial_capital || 100000000,
    position_sizing_type: initialData?.position_sizing_type || 'FIXED_AMOUNT',
    position_size_value: initialData?.position_size_value || 100000000,
    stop_loss_pct: initialData?.stop_loss_pct || undefined,
    take_profit_pct: initialData?.take_profit_pct || undefined,
    date_range_start: initialData?.date_range_start || '2020-01-01',
    date_range_end: initialData?.date_range_end || new Date().toISOString().split('T')[0],
  })

  const handleChange = (field: keyof BacktestConfigCreateRequest, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(formData)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium mb-1">Nama Strategi</label>
        <input
          type="text"
          value={formData.name}
          onChange={(e) => handleChange('name', e.target.value)}
          className="w-full px-3 py-2 border rounded-md"
          placeholder="Contoh: Buy and Hold BBCA"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Kode Saham (Ticker)</label>
        <input
          type="text"
          value={formData.ticker}
          onChange={(e) => handleChange('ticker', e.target.value.toUpperCase())}
          className="w-full px-3 py-2 border rounded-md"
          placeholder="Contoh: BBCA.JK"
          required
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1">Modal Awal (Rp)</label>
          <input
            type="number"
            value={formData.initial_capital}
            onChange={(e) => handleChange('initial_capital', Number(e.target.value))}
            className="w-full px-3 py-2 border rounded-md"
            min={1}
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Jenis Position Sizing</label>
          <select
            value={formData.position_sizing_type}
            onChange={(e) => handleChange('position_sizing_type', e.target.value)}
            className="w-full px-3 py-2 border rounded-md"
          >
            <option value="FIXED_AMOUNT">Jumlah Tetap (Rp)</option>
            <option value="FIXED_PCT">Persentase Modal (%)</option>
            <option value="RISK_BASED">Berdasarkan Risiko (%)</option>
          </select>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">
          Nilai Position Sizing
          {formData.position_sizing_type === 'FIXED_AMOUNT' && ' (Rp)'}
          {formData.position_sizing_type === 'FIXED_PCT' && ' (%)'}
          {formData.position_sizing_type === 'RISK_BASED' && ' (% risiko)'}
        </label>
        <input
          type="number"
          value={formData.position_size_value}
          onChange={(e) => handleChange('position_size_value', Number(e.target.value))}
          className="w-full px-3 py-2 border rounded-md"
          min={1}
          required
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1">Stop Loss (%)</label>
          <input
            type="number"
            value={formData.stop_loss_pct || ''}
            onChange={(e) => handleChange('stop_loss_pct', e.target.value ? Number(e.target.value) : undefined)}
            className="w-full px-3 py-2 border rounded-md"
            min={0}
            max={100}
            step={0.1}
            placeholder="Opsional"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Take Profit (%)</label>
          <input
            type="number"
            value={formData.take_profit_pct || ''}
            onChange={(e) => handleChange('take_profit_pct', e.target.value ? Number(e.target.value) : undefined)}
            className="w-full px-3 py-2 border rounded-md"
            min={0}
            max={1000}
            step={0.1}
            placeholder="Opsional"
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1">Tanggal Mulai</label>
          <input
            type="date"
            value={formData.date_range_start}
            onChange={(e) => handleChange('date_range_start', e.target.value)}
            className="w-full px-3 py-2 border rounded-md"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Tanggal Akhir</label>
          <input
            type="date"
            value={formData.date_range_end}
            onChange={(e) => handleChange('date_range_end', e.target.value)}
            className="w-full px-3 py-2 border rounded-md"
            required
          />
        </div>
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50"
      >
        {isLoading ? 'Menyimpan...' : 'Simpan Konfigurasi'}
      </button>
    </form>
  )
}
