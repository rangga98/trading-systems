import { Stock, OHLCVData } from '../types';
import { ohlcvApi } from '../services/ohlcv';

/**
 * Escapes special Markdown characters in a string to prevent breaking tables.
 */
function escapeMarkdown(text: string): string {
  return text.replace(/[|*]/g, '\\$&');
}

/**
 * Generates a GFM Markdown table for a single stock, including historical data.
 */
export function generateStockMarkdown(stock: Stock, historicalData: OHLCVData[]): string {
  const ticker = escapeMarkdown(stock.ticker);
  const name = escapeMarkdown(stock.name);
  const sector = escapeMarkdown(stock.sector || 'N/A');
  const dataStatus = stock.has_data
    ? `${stock.data_count} data (${stock.date_range?.start} s/d ${stock.date_range?.end})`
    : 'Belum ada data';

  let markdown = `# Data Saham: ${stock.ticker}

## Ringkasan
| Kode | Nama Perusahaan | Sektor | Status Data |
| :--- | :--- | :--- | :--- |
| ${ticker} | ${name} | ${sector} | ${dataStatus} |

## Data Historis
| Tanggal | Buka | Tinggi | Rendah | Tutup | Volume |
| :--- | :--- | :--- | :--- | :--- | :--- |
`;

  historicalData.forEach(row => {
    markdown += `| ${row.date} | ${row.open} | ${row.high} | ${row.low} | ${row.close} | ${row.volume.toLocaleString()} |\n`;
  });

  return markdown;
}

/**
 * Triggers a browser download for a single Markdown file.
 */
function downloadFile(content: string, filename: string) {
  const blob = new Blob([content], { type: 'text/markdown;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', filename);
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

/**
 * Exports multiple stocks as individual Markdown files with a slight delay between downloads.
 */
export async function exportStocksToMarkdown(stocks: Stock[]) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);

  for (const stock of stocks) {
    try {
      // Fetch historical data for the stock
      const response = await ohlcvApi.getData(stock.ticker);
      const historicalData = response.data || [];
      
      const markdown = generateStockMarkdown(stock, historicalData);
      const filename = `${stock.ticker}-export-${timestamp}.md`;
      downloadFile(markdown, filename);
    } catch (error) {
      console.error(`Failed to export data for ${stock.ticker}:`, error);
    }
    
    // Small delay to prevent browser download blocking
    await new Promise(resolve => setTimeout(resolve, 150));
  }
}
