import { apiClient } from './api'

export const exportApi = {
  async downloadCSV(resultId: string): Promise<void> {
    const response = await apiClient.get(
      `/backtests/results/${resultId}/export?format=csv`,
      { responseType: 'blob' }
    )

    // Extract filename from Content-Disposition header
    const contentDisposition = response.headers['content-disposition']
    let filename = 'backtest_export.csv'
    if (contentDisposition) {
      const match = contentDisposition.match(/filename="(.+)"/)
      if (match) filename = match[1]
    }

    // Create download link
    const blob = new Blob([response.data], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  },

  async downloadJSON(resultId: string): Promise<void> {
    const response = await apiClient.get(
      `/backtests/results/${resultId}/export?format=json`,
      { responseType: 'blob' }
    )

    const contentDisposition = response.headers['content-disposition']
    let filename = 'backtest_export.json'
    if (contentDisposition) {
      const match = contentDisposition.match(/filename="(.+)"/)
      if (match) filename = match[1]
    }

    const blob = new Blob([response.data], { type: 'application/json' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  },
}
