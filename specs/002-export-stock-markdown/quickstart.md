# Quickstart: Stock Export Feature

## Overview
This feature allows users to select one or more stocks from the list and export them as individual Markdown files.

## For Users

1.  Navigate to **Daftar Saham** in the sidebar.
2.  Use the checkboxes on the left side of the table to select the stocks you want to export.
3.  Notice that the **Ekspor ke Markdown** button at the top becomes enabled once at least one stock is selected.
4.  Click **Ekspor ke Markdown**.
5.  Your browser will prompt you to download one `.md` file for each stock you selected.
    *   *Note: If you select many stocks, your browser might ask for permission to download multiple files. Please click "Allow".*

## For Developers

### Implementation Details
- **Component**: `DataTable.tsx` updated with `selectable` prop.
- **Page**: `StockListPage.tsx` manages selection state and renders the export button.
- **Utility**: `src/lib/export-utils.ts` (to be created) handles the Markdown generation and download logic.

### Running Tests
Run frontend tests to verify selection logic:
```bash
npm test frontend/src/components/DataTable.test.tsx
```
