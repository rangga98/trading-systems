import { QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { queryClient } from './services/api'

// Placeholder pages - will be implemented later
const Dashboard = () => <div className="p-4">Dashboard (Coming Soon)</div>
const StockImport = () => <div className="p-4">Stock Import (Coming Soon)</div>
const ChartView = () => <div className="p-4">Chart View (Coming Soon)</div>
const Backtest = () => <div className="p-4">Backtest (Coming Soon)</div>

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="min-h-screen bg-background">
          {/* Header */}
          <header className="border-b bg-card px-4 py-3">
            <h1 className="text-xl font-bold">IDX Trading Simulator</h1>
          </header>
          
          {/* Main Content */}
          <main className="p-4">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/stocks" element={<StockImport />} />
              <Route path="/chart" element={<ChartView />} />
              <Route path="/backtest" element={<Backtest />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App
