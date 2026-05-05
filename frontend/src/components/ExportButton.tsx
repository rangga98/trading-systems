import { useState } from 'react'
import { exportApi } from '../services/export'

interface ExportButtonProps {
  resultId: string
  disabled?: boolean
}

export function ExportButton({ resultId, disabled }: ExportButtonProps) {
  const [isExporting, setIsExporting] = useState(false)
  const [showMenu, setShowMenu] = useState(false)

  const handleExport = async (format: 'csv' | 'json') => {
    setIsExporting(true)
    setShowMenu(false)
    try {
      if (format === 'csv') {
        await exportApi.downloadCSV(resultId)
      } else {
        await exportApi.downloadJSON(resultId)
      }
    } catch (error: any) {
      console.error('Export failed:', error)
      alert('Export failed: ' + (error.message || 'Unknown error'))
    } finally {
      setIsExporting(false)
    }
  }

  return (
    <div className="relative inline-block">
      <button
        onClick={() => setShowMenu(!showMenu)}
        disabled={disabled || isExporting}
        className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50 flex items-center gap-2"
      >
        {isExporting ? (
          <>
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
            Exporting...
          </>
        ) : (
          <>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Export
          </>
        )}
      </button>

      {showMenu && (
        <div className="absolute right-0 mt-2 w-48 bg-white border rounded-md shadow-lg z-10">
          <button
            onClick={() => handleExport('csv')}
            className="w-full text-left px-4 py-2 hover:bg-muted first:rounded-t-md"
          >
            <span className="flex items-center gap-2">
              <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Export as CSV
            </span>
          </button>
          <button
            onClick={() => handleExport('json')}
            className="w-full text-left px-4 py-2 hover:bg-muted last:rounded-b-md border-t"
          >
            <span className="flex items-center gap-2">
              <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
              </svg>
              Export as JSON
            </span>
          </button>
        </div>
      )}
    </div>
  )
}
