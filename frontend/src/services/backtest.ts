import { apiClient } from './api'
import type { BacktestConfig, BacktestConfigCreateRequest, BacktestResult } from '../types'

export const backtestApi = {
  // Create backtest config
  async createConfig(data: BacktestConfigCreateRequest): Promise<BacktestConfig> {
    const response = await apiClient.post('/backtests', data)
    return response.data
  },

  // List configs
  async getConfigs(limit: number = 50, offset: number = 0): Promise<{ total: number; items: BacktestConfig[] }> {
    const response = await apiClient.get(`/backtests?limit=${limit}&offset=${offset}`)
    return response.data
  },

  // Get single config
  async getConfig(configId: string): Promise<BacktestConfig> {
    const response = await apiClient.get(`/backtests/${configId}`)
    return response.data
  },

  // Update config
  async updateConfig(configId: string, data: Partial<BacktestConfigCreateRequest>): Promise<BacktestConfig> {
    const response = await apiClient.patch(`/backtests/${configId}`, data)
    return response.data
  },

  // Delete config
  async deleteConfig(configId: string): Promise<void> {
    await apiClient.delete(`/backtests/${configId}`)
  },

  // Execute backtest
  async execute(configId: string): Promise<{ status: string; result_id?: string; message?: string }> {
    const response = await apiClient.post(`/backtests/${configId}/execute`)
    return response.data
  },

  // List results
  async getResults(configId?: string, limit: number = 50, offset: number = 0): Promise<{ total: number; items: BacktestResult[] }> {
    let url = `/backtests/results?limit=${limit}&offset=${offset}`
    if (configId) url += `&config_id=${configId}`
    const response = await apiClient.get(url)
    return response.data
  },

  // Get result detail with trades
  async getResult(resultId: string): Promise<BacktestResult> {
    const response = await apiClient.get(`/backtests/results/${resultId}`)
    return response.data
  },
}
