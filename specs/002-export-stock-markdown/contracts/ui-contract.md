# UI Contract: Stock Export

## DataTable Enhancements

The `DataTable` component will be updated to support row selection.

### New Props
```typescript
interface DataTableProps<T> {
  // ... existing props
  selectable?: boolean;
  selectedIds?: Set<string>;
  onSelectionChange?: (selectedIds: Set<string>) => void;
}
```

### Behavior
- When `selectable` is true, a checkbox column is prepended to the table.
- A "Select All" checkbox is provided in the header.
- `onSelectionChange` is called whenever a checkbox is toggled.

## Export Utility Contract

A new utility or service will handle the Markdown generation and download trigger.

### `exportToMarkdown(stocks: Stock[]): void`
- **Inputs**: Array of `Stock` objects to export.
- **Logic**:
  1. For each stock:
     a. Generate GFM Markdown string.
     b. Create a `Blob` with `type: 'text/markdown'`.
     c. Create a temporary `<a>` element.
     d. Set `download` attribute to `[TICKER]-export-[TIMESTAMP].md`.
     e. Trigger click.
     f. Revoke object URL.
     g. Wait 100ms before next file.
