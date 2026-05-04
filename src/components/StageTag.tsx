import type { TimelineStage } from '../types/news'

const STYLES: Record<TimelineStage, string> = {
  Appears: 'bg-blue-100 text-blue-700 border-blue-200',
  'Picked up': 'bg-violet-100 text-violet-700 border-violet-200',
  Supplemented: 'bg-teal-100 text-teal-700 border-teal-200',
}

export function StageTag({ stage }: { stage: TimelineStage }) {
  return (
    <span
      className={
        'inline-flex rounded-md border px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider ' +
        STYLES[stage]
      }
    >
      {stage}
    </span>
  )
}
