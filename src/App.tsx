import { useMemo, useState } from 'react'
import { artemis } from './data/artemis'
import { PhoneFrame } from './components/PhoneFrame'
import { SearchBar } from './components/SearchBar'
import { BottomTabs, type ViewKey } from './components/BottomTabs'
import { ViewOptionsSheet, type FilterState } from './components/ViewOptionsSheet'
import { CrossSourceView } from './components/views/CrossSourceView'
import { EvidenceTraceView } from './components/views/EvidenceTraceView'
import { ClaimTimelineView } from './components/views/ClaimTimelineView'

function App() {
  const [view, setView] = useState<ViewKey>('cross-source')
  const [query, setQuery] = useState(artemis.title)
  const [optionsOpen, setOptionsOpen] = useState(false)
  const [filters, setFilters] = useState<FilterState>(() => ({
    visibleSourceIds: new Set(artemis.sources.map((s) => s.id)),
    visibleMatchTags: new Set(['shared-facts', 'framing-gaps', 'evidence-support']),
    expandAllEvidence: false,
  }))

  const statusDate = useMemo(
    () =>
      new Date().toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      }),
    [],
  )

  const matchesQuery = query.trim().length === 0 || artemis.title.toLowerCase().includes(query.trim().toLowerCase())

  return (
    <PhoneFrame statusDate={statusDate}>
      <div className="relative flex h-full flex-col">
        <SearchBar
          query={query}
          onQueryChange={setQuery}
          exampleLabel="Minimal mobile-style news comparison"
          onOpenOptions={() => setOptionsOpen(true)}
        />

        <div className="flex-1 overflow-y-auto">
          {!matchesQuery ? (
            <div className="mx-4 mt-4 rounded-xl border border-dashed border-slate-300 bg-slate-50 p-4 text-center text-xs text-slate-500">
              No topics match “{query}”. The loaded example is{' '}
              <span className="font-semibold text-slate-700">{artemis.title}</span>.
            </div>
          ) : view === 'cross-source' ? (
            <CrossSourceView topic={artemis} filters={filters} />
          ) : view === 'evidence' ? (
            <EvidenceTraceView topic={artemis} filters={filters} />
          ) : (
            <ClaimTimelineView topic={artemis} filters={filters} />
          )}
        </div>

        <BottomTabs active={view} onChange={setView} />

        <ViewOptionsSheet
          open={optionsOpen}
          onClose={() => setOptionsOpen(false)}
          sources={artemis.sources}
          filters={filters}
          onFiltersChange={setFilters}
        />
      </div>
    </PhoneFrame>
  )
}

export default App
