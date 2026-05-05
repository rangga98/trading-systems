import axios from 'axios'
import { QueryClient } from '@tanstack/react-query'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
})

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add any auth headers here in the future
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle common errors
    if (error.response?.status === 404) {
      console.error('Resource not found')
    } else if (error.response?.status === 500) {
      console.error('Server error')
    }
    return Promise.reject(error)
  }
)

// TanStack Query client with caching strategy
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60 * 1000, // 1 minute default
      gcTime: 10 * 60 * 1000, // 10 minutes cache lifetime
      retry: 1,
      refetchOnWindowFocus: false,
      refetchOnReconnect: true,
    },
  },
})

// Query key patterns for cache invalidation
export const queryKeys = {
  stocks: {
    all: ['stocks'] as const,
    list: (limit: number, offset: number) => ['stocks', 'list', limit, offset] as const,
    detail: (ticker: string) => ['stocks', 'detail', ticker] as const,
    search: (query: string) => ['stocks', 'search', query] as const,
  },
  ohlcv: {
    data: (ticker: string, timeframe: string) => ['ohlcv', ticker, timeframe] as const,
  },
  backtest: {
    configs: ['backtest', 'configs'] as const,
    config: (id: string) => ['backtest', 'config', id] as const,
    results: ['backtest', 'results'] as const,
    result: (id: string) => ['backtest', 'result', id] as const,
  },
  importJobs: {
    all: ['importJobs'] as const,
    detail: (id: string) => ['importJobs', id] as const,
  },
}

// Cache invalidation helpers
export const invalidateQueries = {
  stocks: () => queryClient.invalidateQueries({ queryKey: ['stocks'] }),
  ohlcv: (ticker: string) => queryClient.invalidateQueries({ queryKey: ['ohlcv', ticker] }),
  backtestConfigs: () => queryClient.invalidateQueries({ queryKey: ['backtest', 'configs'] }),
  backtestResults: () => queryClient.invalidateQueries({ queryKey: ['backtest', 'results'] }),
  all: () => queryClient.invalidateQueries(),
}
