import { QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter, Routes, Route, Link, NavLink } from 'react-router-dom'
import { queryClient } from './services/api'

// Pages
import { StockListPage } from './pages/StockImport/StockListPage'
import { StockImportPage } from './pages/StockImport/StockImportPage'
import { OHLCVViewPage } from './pages/StockImport/OHLCVViewPage'
import { ChartViewPage } from './pages/ChartView/ChartViewPage'
import { BacktestRunPage } from './pages/Backtest/BacktestRunPage'
import { BacktestResultsPage } from './pages/Backtest/BacktestResultsPage'
import { BacktestDetailPage } from './pages/Backtest/BacktestDetailPage'

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
          <main className="flex-1 p-6 overflow-auto">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/stocks" element={<StockListPage />} />
              <Route path="/stocks/import" element={<StockImportPage />} />
              <Route path="/stocks/:ticker" element={<OHLCVViewPage />} />
              <Route path="/chart" element={<ChartViewPage />} />
              <Route path="/backtest/run" element={<BacktestRunPage />} />
<Route path="/backtest/results" element={<BacktestResultsPage />} />
<Route path="/backtest/results/:resultId" element={<BacktestDetailPage />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App
