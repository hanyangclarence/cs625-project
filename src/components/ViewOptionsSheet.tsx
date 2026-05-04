import type { MatchTag, Source } from '../types/news'
import { MATCH_TAG_LABELS } from './MatchTag'

export interface FilterState {
  visibleSourceIds: Set<string>
  visibleMatchTags: Set<MatchTag>
  expandAllEvidence: boolean
}

interface ViewOptionsSheetProps {
  open: boolean
  onClose: () => void
  sources: Source[]
  filters: FilterState
  onFiltersChange: (next: FilterState) => void
}

const ALL_TAGS: MatchTag[] = ['shared-facts', 'framing-gaps', 'evidence-support']

export function ViewOptionsSheet({
  open,
  onClose,
  sources,
  filters,
  onFiltersChange,
}: ViewOptionsSheetProps) {
  if (!open) return null

  function toggleSource(id: string) {
    const next = new Set(filters.visibleSourceIds)
    if (next.has(id)) next.delete(id)
    else next.add(id)
    onFiltersChange({ ...filters, visibleSourceIds: next })
  }

  function toggleTag(tag: MatchTag) {
    const next = new Set(filters.visibleMatchTags)
    if (next.has(tag)) next.delete(tag)
    else next.add(tag)
    onFiltersChange({ ...filters, visibleMatchTags: next })
  }

  return (
    <div className="absolute inset-0 z-20 flex flex-col justify-end">
      <button
        type="button"
        aria-label="Close"
        onClick={onClose}
        className="absolute inset-0 bg-slate-900/30"
      />
      <div className="relative rounded-t-3xl bg-white p-4 shadow-2xl">
        <div className="mx-auto mb-2 h-1 w-10 rounded-full bg-slate-200" />
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-slate-800">View options</h2>
          <button
            type="button"
            onClick={onClose}
            className="text-xs font-medium text-blue-600"
          >
            Done
          </button>
        </div>

        <section className="mb-4">
          <h3 className="mb-2 text-[11px] font-semibold uppercase tracking-wider text-slate-500">
            Sources
          </h3>
          <div className="space-y-1.5">
            {sources.map((s) => (
              <label
                key={s.id}
                className="flex cursor-pointer items-center justify-between rounded-lg bg-slate-50 px-3 py-2 text-xs"
              >
                <span className="font-medium text-slate-700">{s.outlet}</span>
                <input
                  type="checkbox"
                  className="h-4 w-4 accent-blue-600"
                  checked={filters.visibleSourceIds.has(s.id)}
                  onChange={() => toggleSource(s.id)}
                />
              </label>
            ))}
          </div>
        </section>

        <section className="mb-4">
          <h3 className="mb-2 text-[11px] font-semibold uppercase tracking-wider text-slate-500">
            Match tags
          </h3>
          <div className="flex flex-wrap gap-1.5">
            {ALL_TAGS.map((tag) => {
              const on = filters.visibleMatchTags.has(tag)
              return (
                <button
                  key={tag}
                  type="button"
                  onClick={() => toggleTag(tag)}
                  aria-pressed={on}
                  className={
                    'rounded-full border px-2.5 py-1 text-[11px] font-semibold ' +
                    (on
                      ? 'border-blue-500 bg-blue-50 text-blue-700'
                      : 'border-slate-200 bg-white text-slate-400')
                  }
                >
                  {MATCH_TAG_LABELS[tag]}
                </button>
              )
            })}
          </div>
        </section>

        <section>
          <label className="flex cursor-pointer items-center justify-between rounded-lg bg-slate-50 px-3 py-2 text-xs">
            <span className="font-medium text-slate-700">Expand all evidence</span>
            <input
              type="checkbox"
              className="h-4 w-4 accent-blue-600"
              checked={filters.expandAllEvidence}
              onChange={(e) =>
                onFiltersChange({ ...filters, expandAllEvidence: e.target.checked })
              }
            />
          </label>
        </section>
      </div>
    </div>
  )
}
