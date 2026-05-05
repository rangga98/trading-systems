import { useNavigate } from 'react-router-dom'
import { StockImportForm } from '../../components/StockImportForm'

export function StockImportPage() {
  const navigate = useNavigate()

  return (
    <div className="max-w-2xl mx-auto space-y-4">
      <h1 className="text-2xl font-bold">Impor Data Saham</h1>
      <p className="text-muted-foreground">
        Masukkan kode saham IDX (contoh: BBCA.JK) dan rentang tanggal untuk mengimpor data historis.
      </p>
      
      <StockImportForm onSuccess={() => navigate('/stocks')} />
    </div>
  )
}
