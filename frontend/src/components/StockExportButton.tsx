import { useState } from 'react';
import { Stock } from '../types';
import { exportStocksToMarkdown } from '../lib/export-utils';

interface StockExportButtonProps {
  selectedStocks: Stock[];
  disabled?: boolean;
}

export function StockExportButton({ selectedStocks, disabled }: StockExportButtonProps) {
  const [isExporting, setIsExporting] = useState(false);

  const handleExport = async () => {
    if (selectedStocks.length === 0) return;
    
    setIsExporting(true);
    try {
      await exportStocksToMarkdown(selectedStocks);
    } catch (error) {
      console.error('Export failed:', error);
      alert('Gagal mengekspor data. Silakan coba lagi.');
    } finally {
      setIsExporting(false);
    }
  };

  const isDisabled = disabled || isExporting || selectedStocks.length === 0;

  return (
    <button
      onClick={handleExport}
      disabled={isDisabled}
      className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 transition-colors"
      title={selectedStocks.length === 0 ? 'Pilih setidaknya satu saham untuk mengekspor' : ''}
    >
      {isExporting ? (
        <>
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
          Mengekspor...
        </>
      ) : (
        <>
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          Ekspor ke Markdown ({selectedStocks.length})
        </>
      )}
    </button>
  );
}
