import { useMemo } from 'react'
import type { Topic } from '../../types/news'
import type { FilterState } from '../ViewOptionsSheet'
import { StageTag } from '../StageTag'

interface ClaimTimelineViewProps {
  topic: Topic
  filters: FilterState
}

export function ClaimTimelineView({ topic, filters }: ClaimTimelineViewProps) {
  const sourceById = useMemo(
    () => new Map(topic.sources.map((s) => [s.id, s])),
    [topic.sources],
  )
  const claimById = useMemo(
    () => new Map(topic.claims.map((c) => [c.id, c])),
    [topic.claims],
  )

  const entries = topic.timeline
    .filter((e) => filters.visibleSourceIds.has(e.sourceId))
    .slice()
    .sort((a, b) => {
      const byDate = a.date.localeCompare(b.date)
      if (byDate !== 0) return byDate
      const ta = sourceById.get(a.sourceId)?.trustScore ?? 0
      const tb = sourceById.get(b.sourceId)?.trustScore ?? 0
      return tb - ta
    })

  return (
    <div className="px-4 pb-4">
      <div className="mb-3 rounded-2xl bg-slate-900 p-3 text-white">
        <p className="text-[10px] uppercase tracking-widest text-slate-300">Claim timeline</p>
        <h2 className="mt-1 text-base font-semibold leading-tight">{topic.title}</h2>
        <p className="mt-1 text-xs text-slate-300">
          Who said what, in what order — and whether later coverage added or just echoed.
        </p>
      </div>

      <ol className="relative ml-3 space-y-4 border-l-2 border-slate-200 pl-4">
        {entries.map((e) => {
          const source = sourceById.get(e.sourceId)
          const claim = e.claimId ? claimById.get(e.claimId) : undefined
          return (
            <li key={e.id} className="relative">
              <span
                className="absolute -left-[1.4rem] top-1.5 h-3 w-3 rounded-full border-2 border-white bg-blue-500 shadow"
                aria-hidden
              />
              <div className="flex items-center justify-between">
                <time className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">
                  {formatDate(e.date)}
                </time>
                <StageTag stage={e.stage} />
              </div>
              <div className="mt-1 rounded-xl border border-slate-200 bg-white p-3 shadow-sm">
                <p className="text-[11px] font-semibold text-slate-700">
                  {source?.outlet ?? 'Unknown outlet'}
                </p>
                {claim && (
                  <p className="mt-1 text-xs leading-snug text-slate-700">{claim.text}</p>
                )}
                {e.shortNote && (
                  <p className="mt-1.5 text-[11px] leading-snug text-slate-500">{e.shortNote}</p>
                )}
              </div>
            </li>
          )
        })}
        {entries.length === 0 && (
          <li className="text-xs text-slate-500">No timeline entries for the selected sources.</li>
        )}
      </ol>
    </div>
  )
}

function formatDate(iso: string) {
  const d = new Date(iso)
  return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
}
