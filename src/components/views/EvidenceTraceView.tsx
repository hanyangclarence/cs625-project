import { useMemo, useState, useEffect } from 'react'
import type { Claim, EvidenceLink, Source, SupportLevel, Topic } from '../../types/news'
import type { FilterState } from '../ViewOptionsSheet'
import { TrustBadge } from '../TrustBadge'

interface EvidenceTraceViewProps {
  topic: Topic
  filters: FilterState
}

export function EvidenceTraceView({ topic, filters }: EvidenceTraceViewProps) {
  const [expanded, setExpanded] = useState<Set<string>>(new Set())
  const [mode, setMode] = useState<'evidence' | 'credibility'>('evidence')

  useEffect(() => {
    if (filters.expandAllEvidence) {
      setExpanded(new Set(topic.claims.map((c) => c.id)))
    } else {
      setExpanded(new Set())
    }
  }, [filters.expandAllEvidence, topic.claims])

  const sourceById = useMemo(
    () => new Map(topic.sources.map((s) => [s.id, s])),
    [topic.sources],
  )

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
        <p className="text-[10px] uppercase tracking-widest text-slate-300">Evidence trace</p>
        <h2 className="mt-1 text-base font-semibold leading-tight">{topic.title}</h2>
        <p className="mt-1 text-xs text-slate-300">
          Trace every claim back to its source passage and AI trust score.
        </p>
        <div className="mt-3 inline-flex rounded-full bg-slate-800 p-0.5 text-[11px] font-semibold">
          <button
            type="button"
            onClick={() => setMode('evidence')}
            aria-pressed={mode === 'evidence'}
            className={
              'rounded-full px-3 py-1 ' +
              (mode === 'evidence' ? 'bg-white text-slate-900' : 'text-slate-300')
            }
          >
            Claim evidence
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

      {mode === 'evidence' ? (
        <div className="space-y-3">
          {topic.claims.map((c) => (
            <ClaimCard
              key={c.id}
              claim={c}
              sourceById={sourceById}
              visibleSourceIds={filters.visibleSourceIds}
              open={expanded.has(c.id)}
              onToggle={() => toggle(c.id)}
            />
          ))}
        </div>
      ) : (
        <div className="space-y-3">
          {visibleSources.map((s) => (
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
  open,
  onToggle,
}: {
  claim: Claim
  sourceById: Map<string, Source>
  visibleSourceIds: Set<string>
  open: boolean
  onToggle: () => void
}) {
  const evidence = claim.evidence.filter((e) => visibleSourceIds.has(e.sourceId))

  return (
    <article className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
      <button
        type="button"
        onClick={onToggle}
        aria-expanded={open}
        className="flex w-full items-start justify-between gap-3 px-3 py-3 text-left"
      >
        <p className="flex-1 text-sm font-medium leading-snug text-slate-900">{claim.text}</p>
        <TrustBadge label={claim.overallTrust} compact />
      </button>

      {open && (
        <div className="border-t border-slate-100 bg-slate-50 p-3">
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
      <div className="flex items-center justify-between">
        <span className="text-[11px] font-semibold text-slate-700">
          {source?.outlet ?? 'Unknown outlet'}
        </span>
        <span className="text-[11px] font-semibold text-slate-500">{evidence.score}/100</span>
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
          <p className="text-[11px] font-semibold text-slate-700">{source.outlet}</p>
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
