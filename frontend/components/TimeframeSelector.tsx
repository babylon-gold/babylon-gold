'use client'

interface TimeframeSelectorProps {
  selected: string
  onChange: (timeframe: '5min' | '15min' | '1h' | '4h') => void
  disabled?: boolean
}

export default function TimeframeSelector({
  selected,
  onChange,
  disabled = false,
}: TimeframeSelectorProps) {
  const timeframes = [
    { value: '5min', label: '5 دقائق' },
    { value: '15min', label: '15 دقيقة' },
    { value: '1h', label: 'ساعة واحدة' },
    { value: '4h', label: '4 ساعات' },
  ] as const

  return (
    <div className="flex gap-2">
      {timeframes.map(({ value, label }) => (
        <button
          key={value}
          onClick={() => onChange(value as '5min' | '15min' | '1h' | '4h')}
          disabled={disabled}
          className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
            selected === value
              ? 'bg-gold-500 text-slate-900'
              : 'bg-slate-700 text-slate-100 hover:bg-slate-600'
          } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          {label}
        </button>
      ))}
    </div>
  )
}
