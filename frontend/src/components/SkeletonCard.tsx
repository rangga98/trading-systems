export function SkeletonCard({ className = '' }: { className?: string }) {
  return (
    <div className={`animate-pulse bg-card border rounded-lg p-4 space-y-3 ${className}`}>
      <div className="h-4 bg-muted rounded w-3/4" />
      <div className="h-3 bg-muted rounded w-1/2" />
      <div className="h-3 bg-muted rounded w-full" />
    </div>
  )
}

export function SkeletonTable({ rows = 5 }: { rows?: number }) {
  return (
    <div className="border rounded-lg overflow-hidden">
      <div className="bg-muted p-3 flex gap-4">
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="h-4 bg-muted-foreground/20 rounded flex-1" />
        ))}
      </div>
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="p-3 border-t flex gap-4">
          {[1, 2, 3, 4, 5].map((j) => (
            <div key={j} className="h-3 bg-muted rounded flex-1" />
          ))}
        </div>
      ))}
    </div>
  )
}

export function SkeletonChart() {
  return (
    <div className="animate-pulse border rounded-lg p-4 space-y-4">
      <div className="h-6 bg-muted rounded w-1/4" />
      <div className="h-[300px] bg-muted rounded" />
    </div>
  )
}

export function SkeletonForm({ fields = 6 }: { fields?: number }) {
  return (
    <div className="space-y-4 animate-pulse">
      {Array.from({ length: fields }).map((_, i) => (
        <div key={i} className="space-y-2">
          <div className="h-4 bg-muted rounded w-1/4" />
          <div className="h-10 bg-muted rounded" />
        </div>
      ))}
      <div className="h-10 bg-muted rounded w-full" />
    </div>
  )
}
