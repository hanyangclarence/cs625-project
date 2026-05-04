import type { TrustLabel } from '../types/news'

const STYLES: Record<TrustLabel, string> = {
  High: 'bg-emerald-500 text-white',
  Medium: 'bg-amber-500 text-white',
  Low: 'bg-rose-500 text-white',
}

interface TrustBadgeProps {
  label: TrustLabel
  score?: number
  compact?: boolean
}

export function TrustBadge({ label, score, compact }: TrustBadgeProps) {
  return (
    <span
      className={
        'inline-flex items-center gap-1 rounded-full font-semibold ' +
        STYLES[label] +
        (compact ? ' px-2 py-0.5 text-[10px]' : ' px-2.5 py-1 text-[11px]')
      }
    >
      <span>{label}</span>
      {typeof score === 'number' && <span className="opacity-80">· {score}</span>}
    </span>
  )
}
