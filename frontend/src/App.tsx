import { Suspense, lazy } from 'react'
import { QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter, Routes, Route, Link, NavLink, Navigate } from 'react-router-dom'
import { queryClient } from './services/api'
import { ErrorBoundary } from './components/ErrorBoundary'
import { NotificationList } from './components/NotificationList'

// Pages - Lazy loaded for bundle optimization
const StockListPage = lazy(() => import('./pages/StockImport/StockListPage').then(m => ({ default: m.StockListPage })))
const StockImportPage = lazy(() => import('./pages/StockImport/StockImportPage').then(m => ({ default: m.StockImportPage })))
const OHLCVViewPage = lazy(() => import('./pages/StockImport/OHLCVViewPage').then(m => ({ default: m.OHLCVViewPage })))
const ChartViewPage = lazy(() => import('./pages/ChartView/ChartViewPage').then(m => ({ default: m.ChartViewPage })))
const BacktestRunPage = lazy(() => import('./pages/Backtest/BacktestRunPage').then(m => ({ default: m.BacktestRunPage })))
const BacktestResultsPage = lazy(() => import('./pages/Backtest/BacktestResultsPage').then(m => ({ default: m.BacktestResultsPage })))
const BacktestDetailPage = lazy(() => import('./pages/Backtest/BacktestDetailPage').then(m => ({ default: m.BacktestDetailPage })))

// Placeholder pages for future stories
const Dashboard = () => (
  <div className="p-4">
    <h2 className="text-2xl font-bold">Dashboard</h2>
    <p className="text-muted-foreground mt-2">
      Selamat datang di IDX Trading Simulator.
      <br />
      Pilih menu di sidebar untuk memulai.
    </p>
  </div>
)

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="min-h-screen bg-background flex">
          {/* Sidebar */}
          <aside className="w-64 border-r bg-card flex flex-col">
            <div className="p-4 border-b">
              <Link to="/" className="text-xl font-bold">IDX Trading</Link>
            </div>
            <nav className="flex-1 p-4 space-y-2">
              <NavLink
                to="/"
                className={({ isActive }) =>
                  `block px-3 py-2 rounded-md transition-colors ${
                    isActive ? 'bg-primary text-primary-foreground' : 'hover:bg-muted'
                  }`
                }
              >
                Dashboard
              </NavLink>
              <NavLink
                to="/stocks"
                className={({ isActive }) =>
                  `block px-3 py-2 rounded-md transition-colors ${
                    isActive ? 'bg-primary text-primary-foreground' : 'hover:bg-muted'
                  }`
                }
              >
                Daftar Saham
              </NavLink>
              <NavLink
                to="/chart"
                className={({ isActive }) =>
                  `block px-3 py-2 rounded-md transition-colors ${
                    isActive ? 'bg-primary text-primary-foreground' : 'hover:bg-muted'
                  }`
                }
              >
                Grafik
              </NavLink>
              <NavLink
                to="/backtest"
                className={({ isActive }) =>
                  `block px-3 py-2 rounded-md transition-colors ${
                    isActive ? 'bg-primary text-primary-foreground' : 'hover:bg-muted'
                  }`
                }
              >
                Backtest
              </NavLink>
            </nav>
          </aside>

          {/* Main Content */}
          <main className="flex-1 p-6 overflow-auto relative">
            <ErrorBoundary>
              <Suspense fallback={<PageLoading />}>
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/stocks" element={<StockListPage />} />
                  <Route path="/stocks/import" element={<StockImportPage />} />
                  <Route path="/stocks/:ticker" element={<OHLCVViewPage />} />
                  <Route path="/chart" element={<ChartViewPage />} />
                  <Route path="/backtest" element={<Navigate to="/backtest/run" replace />} />
                  <Route path="/backtest/run" element={<BacktestRunPage />} />
                  <Route path="/backtest/results" element={<BacktestResultsPage />} />
                  <Route path="/backtest/results/:resultId" element={<BacktestDetailPage />} />
                </Routes>
              </Suspense>
            </ErrorBoundary>
            <NotificationList />
          </main>
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

function PageLoading() {
  return (
    <div className="flex items-center justify-center min-h-[50vh]">
      <div className="flex items-center gap-3">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
        <span className="text-muted-foreground">Memuat halaman...</span>
      </div>
    </div>
  )
}

export default App
