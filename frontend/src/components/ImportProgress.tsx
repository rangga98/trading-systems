import { useEffect, useState } from 'react'
import { ohlcvApi } from '../services/ohlcv'

interface ImportProgressProps {
  jobId: string
  onComplete?: () => void
  onError?: (error: string) => void
}

export function ImportProgress({ jobId, onComplete, onError }: ImportProgressProps) {
  const [status, setStatus] = useState<string>('PENDING')
  const [progress, setProgress] = useState(0)
  const [recordsImported, setRecordsImported] = useState(0)
  const [recordsTotal, setRecordsTotal] = useState(0)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let interval: NodeJS.Timeout

    const checkProgress = async () => {
      try {
        const job = await ohlcvApi.getImportJob(jobId)
        setStatus(job.status)
        setProgress(job.progress || 0)
        setRecordsImported(job.records_imported || 0)
        setRecordsTotal(job.records_total || 0)

        if (job.error_message) {
          setError(job.error_message)
          onError?.(job.error_message)
          clearInterval(interval)
          return
        }

        if (job.status === 'COMPLETED') {
          onComplete?.()
          clearInterval(interval)
        } else if (job.status === 'FAILED') {
          onError?.('Import job failed')
          clearInterval(interval)
        }
      } catch (err: any) {
        setError(err.message || 'Failed to check job status')
        onError?.(err.message || 'Failed to check job status')
        clearInterval(interval)
      }
    }

    // Check immediately, then every 2 seconds
    checkProgress()
    interval = setInterval(checkProgress, 2000)

    return () => clearInterval(interval)
  }, [jobId, onComplete, onError])

  const getStatusColor = () => {
    switch (status) {
      case 'COMPLETED':
        return 'text-green-600'
      case 'FAILED':
        return 'text-red-600'
      case 'RUNNING':
        return 'text-blue-600'
      default:
        return 'text-gray-600'
    }
  }

  const getStatusText = () => {
    switch (status) {
      case 'PENDING':
        return 'Menunggu...'
      case 'RUNNING':
        return 'Sedang mengimpor...'
      case 'COMPLETED':
        return 'Impor selesai!'
      case 'FAILED':
        return 'Impor gagal'
      default:
        return status
    }
  }

  return (
    <div className="space-y-3 p-4 border rounded-lg bg-card">
      <div className="flex justify-between items-center">
        <span className={`font-medium ${getStatusColor()}`}>
          {getStatusText()}
        </span>
        <span className="text-sm text-muted-foreground">
          {status === 'RUNNING' && `${progress}%`}
        </span>
      </div>

      {/* Progress bar */}
      {status === 'RUNNING' && (
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-primary h-2 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      )}

      {/* Records info */}
      {(status === 'RUNNING' || status === 'COMPLETED') && recordsTotal > 0 && (
        <p className="text-sm text-muted-foreground">
          {recordsImported} dari {recordsTotal} data diimpor
        </p>
      )}

      {/* Success indicator */}
      {status === 'COMPLETED' && (
        <div className="flex items-center gap-2 text-green-600">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
          <span>Data berhasil diimpor</span>
        </div>
      )}

      {/* Error message */}
      {error && (
        <div className="flex items-center gap-2 text-red-600">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
          <span>{error}</span>
        </div>
      )}
    </div>
  )
}
