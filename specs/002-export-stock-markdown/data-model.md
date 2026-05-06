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

## Export Schema (Markdown)

The exported file will contain a table with the following structure:

| Field | Description |
| :--- | :--- |
| Kode | `ticker` |
| Nama | `name` |
| Sektor | `sector` |
| Statistik | Summary of `data_count` and `date_range` |
