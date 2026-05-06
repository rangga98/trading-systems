import { useState } from 'react'

interface Column<T> {
  key: keyof T | string
  header: string
  render?: (item: T) => React.ReactNode
}

interface DataTableProps<T> {
  data: T[]
  columns: Column<T>[]
  keyExtractor: (item: T) => string
  emptyMessage?: string
  selectable?: boolean
  selectedIds?: Set<string>
  onSelectionChange?: (selectedIds: Set<string>) => void
}

export function DataTable<T>({
  data,
  columns,
  keyExtractor,
  emptyMessage = 'Tidak ada data',
  selectable = false,
  selectedIds = new Set(),
  onSelectionChange,
}: DataTableProps<T>) {
  const [sortKey, setSortKey] = useState<string | null>(null)
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc')

  const handleSort = (key: string) => {
    if (sortKey === key) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortKey(key)
      setSortDirection('asc')
    }
  }

  const handleSelectAll = (checked: boolean) => {
    if (!onSelectionChange) return
    if (checked) {
      const allIds = new Set(data.map(keyExtractor))
      onSelectionChange(allIds)
    } else {
      onSelectionChange(new Set())
    }
  }

  const handleSelectRow = (id: string, checked: boolean) => {
    if (!onSelectionChange) return
    const nextSelected = new Set(selectedIds)
    if (checked) {
      nextSelected.add(id)
    } else {
      nextSelected.delete(id)
    }
    onSelectionChange(nextSelected)
  }

  if (data.length === 0) {
    return (
      <div className="p-8 text-center text-muted-foreground border rounded-lg">
        {emptyMessage}
      </div>
    )
  }

  const isAllSelected = data.length > 0 && data.every(item => selectedIds.has(keyExtractor(item)))

  return (
    <div className="overflow-x-auto border rounded-lg">
      <table className="w-full text-sm">
        <thead className="bg-muted">
          <tr>
            {selectable && (
              <th className="px-4 py-3 w-10">
                <input
                  type="checkbox"
                  className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                  checked={isAllSelected}
                  onChange={(e) => handleSelectAll(e.target.checked)}
                />
              </th>
            )}
            {columns.map((col) => (
              <th
                key={String(col.key)}
                className="px-4 py-3 text-left font-medium cursor-pointer hover:bg-muted/80"
                onClick={() => handleSort(String(col.key))}
              >
                {col.header}
                {sortKey === col.key && (
                  <span className="ml-1">
                    {sortDirection === 'asc' ? '↑' : '↓'}
                  </span>
                )}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((item) => (
            <tr key={keyExtractor(item)} className="border-t hover:bg-muted/50">
              {selectable && (
                <td className="px-4 py-3">
                  <input
                    type="checkbox"
                    className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                    checked={selectedIds.has(keyExtractor(item))}
                    onChange={(e) => handleSelectRow(keyExtractor(item), e.target.checked)}
                  />
                </td>
              )}
              {columns.map((col) => (
                <td key={String(col.key)} className="px-4 py-3">
                  {col.render
                    ? col.render(item)
                    : String((item as any)[col.key] ?? '-')}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
