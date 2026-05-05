import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { BacktestConfigForm } from '../../components/BacktestForm'
import { backtestApi } from '../../services/backtest'
import type { BacktestConfigCreateRequest } from '../../types'

export function BacktestRunPage() {
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  const createMutation = useMutation({
    mutationFn: backtestApi.createConfig,
    onSuccess: (data) => {
      setSuccessMessage(`Konfigurasi "${data.name}" berhasil disimpan!`)
      // Optionally auto-execute
    },
  })

  const handleSubmit = (data: BacktestConfigCreateRequest) => {
    setSuccessMessage(null)
    createMutation.mutate(data)
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Backtest - Konfigurasi</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Buat konfigurasi backtest untuk mengevaluasi strategi trading
        </p>
      </div>

      {successMessage && (
        <div className="p-4 bg-green-50 border border-green-200 rounded-lg text-green-800">
          {successMessage}
        </div>
      )}

      {createMutation.isError && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-800">
          Error: {(createMutation.error as Error).message}
        </div>
      )}

      <div className="max-w-2xl">
        <BacktestConfigForm
          onSubmit={handleSubmit}
          isLoading={createMutation.isPending}
        />
      </div>
    </div>
  )
}
