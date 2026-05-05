interface EmptyStateProps {
  title?: string
  description?: string
  action?: {
    label: string
    onClick: () => void
  }
  icon?: string
}

export function EmptyState({
  title = 'Tidak Ada Data',
  description = 'Belum ada data yang tersedia.',
  action,
  icon = '📭',
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center border rounded-lg bg-card">
      <div className="text-4xl mb-3">{icon}</div>
      <h3 className="text-lg font-semibold text-foreground">{title}</h3>
      <p className="text-sm text-muted-foreground mt-1 max-w-sm">{description}</p>
      {action && (
        <button
          onClick={action.onClick}
          className="mt-4 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 text-sm"
        >
          {action.label}
        </button>
      )}
    </div>
  )
}
