import { useState } from 'react'
import type { Source, Topic } from '../../types/news'
import type { FilterState } from '../ViewOptionsSheet'
import { MatchTagChip } from '../MatchTag'

interface CrossSourceViewProps {
  topic: Topic
  filters: FilterState
}

export function CrossSourceView({ topic, filters }: CrossSourceViewProps) {
  const [openId, setOpenId] = useState<string | null>(null)

  const sources = topic.sources.filter(
    (s) => filters.visibleSourceIds.has(s.id) && filters.visibleMatchTags.has(s.matchTag),
  )

  return (
    <div className="px-4 pb-4">
      <div className="mb-3 rounded-2xl bg-slate-900 p-3 text-white">
        <p className="text-[10px] uppercase tracking-widest text-slate-300">Cross-source view</p>
        <h2 className="mt-1 text-base font-semibold leading-tight">{topic.title}</h2>
        <p className="mt-1 text-xs text-slate-300">
          Compare how {sources.length} outlets report the same event side-by-side.
        </p>
      </div>

      {sources.length === 0 && (
        <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50 p-4 text-center text-xs text-slate-500">
          No sources match the current filters. Open View options to restore.
        </div>
      )}

      <div className="space-y-3">
        {sources.map((s) => (
          <SourceCard
            key={s.id}
            source={s}
            topic={topic}
            open={openId === s.id}
            onToggle={() => setOpenId(openId === s.id ? null : s.id)}
          />
        ))}
      </div>
    </div>
  )
}

function SourceCard({
  source,
  topic,
  open,
  onToggle,
}: {
  source: Source
  topic: Topic
  open: boolean
  onToggle: () => void
}) {
  const claimsCovered = topic.claims.filter((c) =>
    c.evidence.some((e) => e.sourceId === source.id),
  )

  return (
    <article className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
      <button
        type="button"
        onClick={onToggle}
        aria-expanded={open}
        className="block w-full text-left"
      >
        {source.imageUrl && (
          <div className="h-28 w-full overflow-hidden bg-slate-100">
            <img
              src={source.imageUrl}
              alt=""
              className="h-full w-full object-cover"
              loading="lazy"
            />
          </div>
        )}
        <div className="p-3">
          <div className="flex items-center justify-between text-[11px] text-slate-500">
            <span className="font-semibold text-slate-700">{source.outlet}</span>
            <span>{formatDate(source.date)}</span>
          </div>
          <h3 className="mt-1 text-sm font-semibold leading-snug text-slate-900">
            {source.articleTitle}
          </h3>
          <div className="mt-2 flex items-center justify-between">
            <MatchTagChip tag={source.matchTag} />
            <span className="text-[11px] font-semibold text-slate-600">
              {source.matchScore}/100
            </span>
          </div>
        </div>
      </button>

      {open && (
        <div className="border-t border-slate-100 bg-slate-50 px-3 py-2.5">
          <p className="text-[11px] uppercase tracking-widest text-slate-500">Covers claims</p>
          <ul className="mt-1.5 space-y-1.5">
            {claimsCovered.map((c) => (
              <li
                key={c.id}
                className="rounded-md bg-white px-2.5 py-1.5 text-xs leading-snug text-slate-700 shadow-sm"
              >
                {c.text}
              </li>
            ))}
            {claimsCovered.length === 0 && (
              <li className="text-xs text-slate-500">No tracked claims from this source.</li>
            )}
          </ul>
        </div>
      )}
    </article>
  )
}

function formatDate(iso: string) {
  const d = new Date(iso)
  return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
}
