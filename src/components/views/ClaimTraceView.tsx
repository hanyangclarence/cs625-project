import { useMemo, useState } from 'react'
import type { Claim, EvidenceLink, Source, SupportLevel, TimelineEntry, Topic } from '../../types/news'
import type { FilterState } from '../ViewOptionsSheet'
import { TrustBadge } from '../TrustBadge'
import { StageTag } from '../StageTag'
import { ExternalLink } from '../ExternalLink'

interface ClaimTraceViewProps {
  topic: Topic
  filters: FilterState
  query?: string
}

function claimMatchesQuery(c: Claim, q: string): boolean {
  if (!q) return true
  const needle = q.toLowerCase()
  if (c.text.toLowerCase().includes(needle)) return true
  return c.evidence.some((e) => e.passage.toLowerCase().includes(needle))
}

function sourceMatchesQuery(s: Source, q: string): boolean {
  if (!q) return true
  const needle = q.toLowerCase()
  return (
    s.outlet.toLowerCase().includes(needle) ||
    s.articleTitle.toLowerCase().includes(needle) ||
    s.summary.toLowerCase().includes(needle)
  )
}

export function ClaimTraceView({ topic, filters, query = '' }: ClaimTraceViewProps) {
  const [expanded, setExpanded] = useState<Set<string>>(new Set())
  const [mode, setMode] = useState<'claim' | 'credibility'>('claim')

  const effectiveExpanded = filters.expandAllEvidence
    ? new Set(topic.claims.map((c) => c.id))
    : expanded

  const sourceById = useMemo(
    () => new Map(topic.sources.map((s) => [s.id, s])),
    [topic.sources],
  )

  const timelineByClaim = useMemo(() => {
    const map = new Map<string, TimelineEntry[]>()
    for (const e of topic.timeline) {
      if (!e.claimId) continue
      const list = map.get(e.claimId) ?? []
      list.push(e)
      map.set(e.claimId, list)
    }
    for (const list of map.values()) {
      list.sort((a, b) => {
        const byDate = a.date.localeCompare(b.date)
        if (byDate !== 0) return byDate
        const ta = sourceById.get(a.sourceId)?.trustScore ?? 0
        const tb = sourceById.get(b.sourceId)?.trustScore ?? 0
        return tb - ta
      })
    }
    return map
  }, [topic.timeline, sourceById])

  function toggle(id: string) {
    const next = new Set(expanded)
    if (next.has(id)) next.delete(id)
    else next.add(id)
    setExpanded(next)
  }

  const visibleSources = topic.sources.filter((s) => filters.visibleSourceIds.has(s.id))

  return (
    <div className="px-4 pb-4">
      <div className="mb-3 rounded-2xl bg-slate-900 p-3 text-white">
        <p className="text-[10px] uppercase tracking-widest text-slate-300">Claim trace</p>
        <h2 className="mt-1 text-base font-semibold leading-tight">{topic.title}</h2>
        <p className="mt-1 text-xs text-slate-300">
          For each claim: who supports it, with what passages, and how the reporting unfolded over time.
        </p>
        <div className="mt-3 inline-flex rounded-full bg-slate-800 p-0.5 text-[11px] font-semibold">
          <button
            type="button"
            onClick={() => setMode('claim')}
            aria-pressed={mode === 'claim'}
            className={
              'rounded-full px-3 py-1 ' +
              (mode === 'claim' ? 'bg-white text-slate-900' : 'text-slate-300')
            }
          >
            Claim trace
          </button>
          <button
            type="button"
            onClick={() => setMode('credibility')}
            aria-pressed={mode === 'credibility'}
            className={
              'rounded-full px-3 py-1 ' +
              (mode === 'credibility' ? 'bg-white text-slate-900' : 'text-slate-300')
            }
          >
            News credibility
          </button>
        </div>
      </div>

      {mode === 'claim' ? (
        <div className="space-y-3">
          {topic.claims
            .filter((c) => claimMatchesQuery(c, query.trim()))
            .map((c) => (
              <ClaimCard
                key={c.id}
                claim={c}
                sourceById={sourceById}
                visibleSourceIds={filters.visibleSourceIds}
                timelineEntries={timelineByClaim.get(c.id) ?? []}
                open={effectiveExpanded.has(c.id)}
                onToggle={() => toggle(c.id)}
              />
            ))}
          {topic.claims.filter((c) => claimMatchesQuery(c, query.trim())).length === 0 && (
            <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50 p-4 text-center text-xs text-slate-500">
              No claims match “{query}”.
            </div>
          )}
        </div>
      ) : (
        <div className="space-y-3">
          {visibleSources
            .filter((s) => sourceMatchesQuery(s, query.trim()))
            .map((s) => (
              <CredibilityCard key={s.id} source={s} />
            ))}
          {visibleSources.length === 0 && (
            <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50 p-4 text-center text-xs text-slate-500">
              No sources selected.
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function ClaimCard({
  claim,
  sourceById,
  visibleSourceIds,
  timelineEntries,
  open,
  onToggle,
}: {
  claim: Claim
  sourceById: Map<string, Source>
  visibleSourceIds: Set<string>
  timelineEntries: TimelineEntry[]
  open: boolean
  onToggle: () => void
}) {
  const evidence = claim.evidence.filter((e) => visibleSourceIds.has(e.sourceId))
  const visibleTimeline = timelineEntries.filter((e) => visibleSourceIds.has(e.sourceId))

  return (
    <article className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
      <button
        type="button"
        onClick={onToggle}
        aria-expanded={open}
        className="flex w-full items-start justify-between gap-3 px-3 py-3 text-left"
      >
        <div className="flex-1">
          <p className="text-sm font-medium leading-snug text-slate-900">{claim.text}</p>
          <p className="mt-1 text-[11px] text-slate-500">
            {evidence.length} passage{evidence.length === 1 ? '' : 's'}
            {visibleTimeline.length > 0 && (
              <> · {visibleTimeline.length} report{visibleTimeline.length === 1 ? '' : 's'}</>
            )}
          </p>
        </div>
        <TrustBadge label={claim.overallTrust} compact />
      </button>

      {open && (
        <div className="border-t border-slate-100 bg-slate-50 p-3">
          <section>
            <h4 className="mb-2 text-[10px] font-semibold uppercase tracking-widest text-slate-500">
              Supporting passages
            </h4>
            <ul className="space-y-2">
              {evidence.map((e, i) => (
                <EvidencePassage
                  key={`${e.sourceId}-${i}`}
                  evidence={e}
                  source={sourceById.get(e.sourceId)}
                />
              ))}
              {evidence.length === 0 && (
                <li className="text-xs text-slate-500">
                  No supporting passages from currently visible sources.
                </li>
              )}
            </ul>
          </section>

          {visibleTimeline.length > 0 && (
            <section className="mt-4">
              <h4 className="mb-2 text-[10px] font-semibold uppercase tracking-widest text-slate-500">
                Reporting timeline
              </h4>
              <ol className="relative ml-2 space-y-3 border-l-2 border-slate-200 pl-4">
                {visibleTimeline.map((e) => {
                  const source = sourceById.get(e.sourceId)
                  return (
                    <li key={e.id} className="relative">
                      <span
                        className="absolute -left-[1.4rem] top-1.5 h-3 w-3 rounded-full border-2 border-slate-50 bg-blue-500 shadow"
                        aria-hidden
                      />
                      <div className="flex items-center justify-between">
                        <time className="text-[10px] font-semibold uppercase tracking-wider text-slate-500">
                          {formatDate(e.date)}
                        </time>
                        <StageTag stage={e.stage} />
                      </div>
                      <div className="mt-1 rounded-lg bg-white p-2.5 shadow-sm">
                        <div className="flex items-center justify-between gap-2">
                          <p className="text-[11px] font-semibold text-slate-700">
                            {source?.outlet ?? 'Unknown outlet'}
                          </p>
                          {source?.url && <ExternalLink href={source.url} />}
                        </div>
                        {e.shortNote && (
                          <p className="mt-1 text-[11px] leading-snug text-slate-500">
                            {e.shortNote}
                          </p>
                        )}
                      </div>
                    </li>
                  )
                })}
              </ol>
            </section>
          )}
        </div>
      )}
    </article>
  )
}

const SUPPORT_COLORS: Record<SupportLevel, { bar: string; label: string; text: string }> = {
  strong: { bar: 'bg-emerald-500', label: 'Strong support', text: 'text-emerald-700' },
  partial: { bar: 'bg-amber-500', label: 'Partial support', text: 'text-amber-700' },
  weaker: { bar: 'bg-rose-500', label: 'Weak support', text: 'text-rose-700' },
}

function EvidencePassage({ evidence, source }: { evidence: EvidenceLink; source?: Source }) {
  const color = SUPPORT_COLORS[evidence.supportLevel]
  return (
    <li className="rounded-xl bg-white p-3 shadow-sm">
      <div className="flex items-center justify-between gap-2">
        <span className="text-[11px] font-semibold text-slate-700">
          {source?.outlet ?? 'Unknown outlet'}
        </span>
        <div className="flex items-center gap-2">
          <span className="text-[11px] font-semibold text-slate-500">{evidence.score}/100</span>
          {source?.url && <ExternalLink href={source.url} />}
        </div>
      </div>
      <p className="mt-1.5 text-xs leading-snug text-slate-700">“{evidence.passage}”</p>
      <div className="mt-2 flex items-center gap-2">
        <span className={'inline-block h-1.5 w-12 rounded-full ' + color.bar} />
        <span className={'text-[10px] font-semibold uppercase tracking-wider ' + color.text}>
          {color.label}
        </span>
      </div>
    </li>
  )
}

function CredibilityCard({ source }: { source: Source }) {
  const total = source.rubric.references + source.rubric.authority + source.rubric.clarity
  return (
    <article className="rounded-2xl border border-slate-200 bg-white p-3 shadow-sm">
      <div className="flex items-start justify-between gap-2">
        <div>
          <div className="flex items-center gap-2">
            <p className="text-[11px] font-semibold text-slate-700">{source.outlet}</p>
            {source.url && <ExternalLink href={source.url} />}
          </div>
          <p className="mt-0.5 text-xs leading-snug text-slate-600">{source.articleTitle}</p>
        </div>
        <TrustBadge label={source.trustLabel} score={total} />
      </div>
      <p className="mt-2 text-[11px] leading-snug text-slate-500">{source.summary}</p>
      <dl className="mt-3 grid grid-cols-3 gap-2 text-center">
        <RubricCell label="References" value={source.rubric.references} />
        <RubricCell label="Authority" value={source.rubric.authority} />
        <RubricCell label="Clarity" value={source.rubric.clarity} />
      </dl>
    </article>
  )
}

function RubricCell({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-lg bg-slate-50 px-2 py-1.5">
      <dt className="text-[9px] font-semibold uppercase tracking-wider text-slate-400">{label}</dt>
      <dd className="mt-0.5 text-sm font-semibold text-slate-800">
        {value}
        <span className="text-[10px] font-normal text-slate-400"> /30</span>
      </dd>
    </div>
  )
}

function formatDate(iso: string) {
  const d = new Date(iso)
  return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
}
