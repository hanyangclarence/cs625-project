import type { MatchTag as MatchTagKind } from '../types/news'

const STYLES: Record<MatchTagKind, { label: string; classes: string }> = {
  'shared-facts': {
    label: 'SHARED FACTS',
    classes: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  },
  'framing-gaps': {
    label: 'FRAMING GAPS',
    classes: 'bg-amber-50 text-amber-700 border-amber-200',
  },
  'evidence-support': {
    label: 'EVIDENCE SUPPORT',
    classes: 'bg-sky-50 text-sky-700 border-sky-200',
  },
}

export function MatchTagChip({ tag }: { tag: MatchTagKind }) {
  const style = STYLES[tag]
  return (
    <span
      className={
        'inline-flex items-center rounded-full border px-2 py-0.5 text-[10px] font-semibold tracking-wider ' +
        style.classes
      }
    >
      {style.label}
    </span>
  )
}

export const MATCH_TAG_LABELS: Record<MatchTagKind, string> = {
  'shared-facts': 'Shared facts',
  'framing-gaps': 'Framing gaps',
  'evidence-support': 'Evidence support',
}
