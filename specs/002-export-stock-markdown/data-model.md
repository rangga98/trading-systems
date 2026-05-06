# Data Model: Stock Export

This feature primarily uses the existing `Stock` entity but introduces transient state for selection and export management.

## Existing Entities

### Stock (from `backend/app/models/stock.py`)
| Field | Type | Description |
| :--- | :--- | :--- |
| id | UUID | Primary Key |
| ticker | String | Stock ticker symbol (e.g., BBCA) |
| name | String | Company name |
| sector | String | Industry sector |

## UI State (Transient)

### SelectedStockIds
- **Type**: `Set<string>` (Frontend state)
- **Description**: Stores the IDs of stocks currently selected by the user in the `StockListPage`.

### HistoricalData
Table of OHLCV data for the stock.
| Field | Type | Description |
| :--- | :--- | :--- |
| Tanggal | String | YYYY-MM-DD |
| Buka | Number | Open price |
| Tinggi | Number | High price |
| Rendah | Number | Low price |
| Tutup | Number | Close price |
| Volume | Number | Trading volume |

## Export Schema (Markdown)

The exported file will contain a table with the following structure:

| Field | Description |
| :--- | :--- |
| Kode | `ticker` |
| Nama | `name` |
| Sektor | `sector` |
| Statistik | Summary of `data_count` and `date_range` |
| Historical Data | Table of OHLCV data for the stock |
