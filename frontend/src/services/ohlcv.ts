import { apiClient } from './api'
import type { OHLCVResponse, OHLCVImportRequest, ImportJob } from '../types'

export const ohlcvApi = {
  // Get OHLCV data for a stock
  async getData(
    ticker: string,
    params?: {
      start_date?: string
      end_date?: string
      timeframe?: 'daily' | 'weekly' | 'monthly'
      limit?: number
      offset?: number
    }
  ): Promise<OHLCVResponse> {
    const searchParams = new URLSearchParams()
    if (params?.start_date) searchParams.append('start_date', params.start_date)
    if (params?.end_date) searchParams.append('end_date', params.end_date)
    if (params?.timeframe) searchParams.append('timeframe', params.timeframe)
    if (params?.limit) searchParams.append('limit', String(params.limit))
    if (params?.offset !== undefined) searchParams.append('offset', String(params.offset))
    
    const query = searchParams.toString()
    const url = query ? `/stocks/${ticker}/ohlcv?${query}` : `/stocks/${ticker}/ohlcv`
    
    const response = await apiClient.get(url)
    return response.data
  },

  // Import OHLCV data
  async importData(
    ticker: string,
    data: OHLCVImportRequest
  ): Promise<{ status: string; ticker: string; records_imported: number; records_skipped: number; records_updated: number }> {
    const response = await apiClient.post(`/stocks/${ticker}/ohlcv/import`, data)
    return response.data
  },

  // Get import job status
  async getImportJob(jobId: string): Promise<ImportJob> {
    const response = await apiClient.get(`/import-jobs/${jobId}`)
    return response.data
  },
}
