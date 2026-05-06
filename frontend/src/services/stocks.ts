import { apiClient } from './api'
import type { Stock, StockCreateRequest, StockListResponse } from '../types'

export const stocksApi = {
  // List all stocks with optional filtering
  async getAll(
    search?: string,
    hasData?: boolean,
    limit: number = 50,
    offset: number = 0
  ): Promise<StockListResponse> {
    const params = new URLSearchParams()
    if (search) params.append('search', search)
    if (hasData !== undefined) params.append('has_data', String(hasData))
    params.append('limit', String(limit))
    params.append('offset', String(offset))
    
    const response = await apiClient.get(`/stocks?${params.toString()}`)
    return response.data
  },

  // Get single stock by ticker
  async getByTicker(ticker: string): Promise<Stock> {
    const response = await apiClient.get(`/stocks/${ticker}`)
    return response.data
  },

  // Create new stock
  async create(data: StockCreateRequest): Promise<Stock> {
    const response = await apiClient.post('/stocks', data)
    return response.data
  },

  // Delete stock
  async delete(stockId: string, hard: boolean = false): Promise<void> {
    await apiClient.delete(`/stocks/${stockId}?hard=${hard}`)
  },
}
