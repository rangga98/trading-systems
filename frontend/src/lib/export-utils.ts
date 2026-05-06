import { Stock } from '../types';

/**
 * Escapes special Markdown characters in a string to prevent breaking tables.
 */
function escapeMarkdown(text: string): string {
  return text.replace(/[|*]/g, '\\$&');
}

/**
 * Generates a GFM Markdown table for a single stock.
 */
export function generateStockMarkdown(stock: Stock): string {
  const ticker = escapeMarkdown(stock.ticker);
  const name = escapeMarkdown(stock.name);
  const sector = escapeMarkdown(stock.sector || 'N/A');
  const dataStatus = stock.has_data
    ? `${stock.data_count} data (${stock.date_range?.start} s/d ${stock.date_range?.end})`
    : 'Belum ada data';

  return `# Data Saham: ${stock.ticker}

| Kode | Nama Perusahaan | Sektor | Status Data |
| :--- | :--- | :--- | :--- |
| ${ticker} | ${name} | ${sector} | ${dataStatus} |
`;
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
    const markdown = generateStockMarkdown(stock);
    const filename = `${stock.ticker}-export-${timestamp}.md`;
    downloadFile(markdown, filename);
    
    // Small delay to prevent browser download blocking
    await new Promise(resolve => setTimeout(resolve, 150));
  }
}
