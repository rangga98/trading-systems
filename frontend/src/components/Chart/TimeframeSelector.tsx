interface TimeframeSelectorProps {
  value: 'daily' | 'weekly' | 'monthly'
  onChange: (timeframe: 'daily' | 'weekly' | 'monthly') => void
  disabled?: boolean
}

export function TimeframeSelector({ value, onChange, disabled }: TimeframeSelectorProps) {
  const timeframes = [
    { value: 'daily', label: 'Harian' },
    { value: 'weekly', label: 'Mingguan' },
    { value: 'monthly', label: 'Bulanan' },
  ] as const

  return (
    <div className="flex gap-1 p-1 bg-muted rounded-lg">
      {timeframes.map((tf) => (
        <button
          key={tf.value}
          onClick={() => onChange(tf.value)}
          disabled={disabled}
          className={`px-3 py-1 text-sm rounded-md transition-colors ${
            value === tf.value
              ? 'bg-primary text-primary-foreground'
              : 'hover:bg-muted-foreground/10'
          } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          {tf.label}
        </button>
      ))}
    </div>
  )
}
