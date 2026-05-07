import { useEffect, useMemo, useRef, useState } from 'react'
import { artemis as artemisFallback } from './data/artemis'
import type { Topic } from './types/news'
import { PhoneFrame } from './components/PhoneFrame'
import { SearchBar } from './components/SearchBar'
import { BottomTabs, type ViewKey } from './components/BottomTabs'
import { ViewOptionsSheet, type FilterState } from './components/ViewOptionsSheet'
import { CrossSourceView } from './components/views/CrossSourceView'
import { ClaimTraceView } from './components/views/ClaimTraceView'
import { RunProgress } from './components/RunProgress'

function topicIdFromUrl(): string {
  if (typeof window === 'undefined') return artemisFallback.id
  const params = new URLSearchParams(window.location.search)
  return params.get('t')?.trim() || artemisFallback.id
}

function topicUrl(id: string): string {
  return `${import.meta.env.BASE_URL}data/${id}.json`
}

// Mirror of backend `_slugify` in newslens/api.py and newslens/cli.py.
function slugify(text: string): string {
  let s = text.toLowerCase().replace(/[^a-z0-9]+/g, '-')
  s = s.replace(/^-+|-+$/g, '')
  s = s.replace(/-+/g, '-')
  return s || 'topic'
}

async function loadTopicIfPresent(id: string): Promise<Topic | null> {
  try {
    const r = await fetch(topicUrl(id))
    if (!r.ok) return null
    const ct = r.headers.get('content-type') || ''
    // Vite's dev/preview SPA fallback returns index.html for missing routes;
    // require a JSON content-type to consider this a real hit.
    if (!ct.includes('application/json')) return null
    return (await r.json()) as Topic
  } catch {
    return null
  }
}

function setUrlTopic(id: string) {
  if (typeof window === 'undefined') return
  const url = new URL(window.location.href)
  url.searchParams.set('t', id)
  window.history.replaceState({}, '', url.toString())
}

interface RunState {
  jobId: string
  topicId: string
  topic: string
  status: 'running' | 'error'
  progress: string[]
  error?: string | null
}

function App() {
  const [topic, setTopic] = useState<Topic>(artemisFallback)
  const [view, setView] = useState<ViewKey>('cross-source')
  const [query, setQuery] = useState('')
  const [optionsOpen, setOptionsOpen] = useState(false)
  const [filters, setFilters] = useState<FilterState>(() => ({
    visibleSourceIds: new Set(artemisFallback.sources.map((s) => s.id)),
    visibleMatchTags: new Set(['shared-facts', 'framing-gaps', 'evidence-support']),
    expandAllEvidence: false,
  }))
  const [run, setRun] = useState<RunState | null>(null)
  const pollTimer = useRef<number | null>(null)

  function applyTopic(data: Topic) {
    setTopic(data)
    setFilters({
      visibleSourceIds: new Set(data.sources.map((s) => s.id)),
      visibleMatchTags: new Set(['shared-facts', 'framing-gaps', 'evidence-support']),
      expandAllEvidence: false,
    })
    setQuery('')
  }

  useEffect(() => {
    let cancelled = false
    const id = topicIdFromUrl()
    fetch(topicUrl(id))
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then((data: Topic) => {
        if (cancelled) return
        applyTopic(data)
      })
      .catch(() => {
        // Backend output not present; silently keep the bundled fallback.
      })
    return () => {
      cancelled = true
    }
  }, [])

  function stopPolling() {
    if (pollTimer.current !== null) {
      window.clearInterval(pollTimer.current)
      pollTimer.current = null
    }
  }

  useEffect(() => {
    return () => stopPolling()
  }, [])

  async function startRun(rawTopic: string) {
    // Block re-entry while a run is already in flight.
    if (run?.status === 'running') return
    stopPolling()

    const slug = slugify(rawTopic)

    // Set running state synchronously so the Run button locks immediately,
    // closing the race window with the API call below.
    setRun({
      jobId: '',
      topicId: slug,
      topic: rawTopic,
      status: 'running',
      progress: ['[checking] looking for cached topic...'],
    })

    // If we already have this topic JSON on disk, just load it — no pipeline run.
    const existing = await loadTopicIfPresent(slug)
    if (existing) {
      applyTopic(existing)
      setUrlTopic(slug)
      setRun(null)
      return
    }

    let job: { job_id: string; topic_id: string }
    try {
      const r = await fetch('/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic: rawTopic }),
      })
      if (!r.ok) throw new Error(`API ${r.status}`)
      job = await r.json()
    } catch {
      setRun({
        jobId: '',
        topicId: slug,
        topic: rawTopic,
        status: 'error',
        progress: [],
        error:
          'Could not reach the backend at /api/run. Start it with: ' +
          'uvicorn newslens.api:app --port 8787',
      })
      return
    }

    setRun((prev) =>
      prev
        ? {
            ...prev,
            jobId: job.job_id,
            topicId: job.topic_id,
            progress: ['[queued] pipeline starting...'],
          }
        : prev,
    )

    pollTimer.current = window.setInterval(async () => {
      try {
        const r = await fetch(`/api/jobs/${job.job_id}`)
        if (!r.ok) return
        const data = await r.json()
        setRun((prev) =>
          prev
            ? {
                ...prev,
                progress: data.progress ?? prev.progress,
                status: data.status === 'error' ? 'error' : prev.status,
                error: data.error ?? prev.error ?? null,
              }
            : prev,
        )
        if (data.status === 'done') {
          stopPolling()
          const tdata = await fetch(topicUrl(job.topic_id)).then((r2) => r2.json())
          applyTopic(tdata)
          setUrlTopic(job.topic_id)
          setRun(null)
        } else if (data.status === 'error') {
          stopPolling()
        }
      } catch {
        // network blip — keep polling
      }
    }, 2000)
  }

  const statusDate = useMemo(
    () =>
      new Date().toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      }),
    [],
  )

  return (
    <PhoneFrame statusDate={statusDate}>
      <div className="relative flex h-full flex-col">
        <SearchBar
          query={query}
          onQueryChange={setQuery}
          exampleLabel={topic.title}
          onOpenOptions={() => setOptionsOpen(true)}
          onSubmit={startRun}
          submitDisabled={run?.status === 'running'}
        />

        <div className="flex-1 overflow-y-auto">
          {view === 'cross-source' ? (
            <CrossSourceView topic={topic} filters={filters} query={query} />
          ) : (
            <ClaimTraceView topic={topic} filters={filters} query={query} />
          )}
        </div>

        <BottomTabs active={view} onChange={setView} />

        <ViewOptionsSheet
          open={optionsOpen}
          onClose={() => setOptionsOpen(false)}
          sources={topic.sources}
          filters={filters}
          onFiltersChange={setFilters}
        />

        {run && (
          <RunProgress
            topic={run.topic}
            status={run.status}
            progress={run.progress}
            error={run.error}
            onCancel={() => {
              stopPolling()
              setRun(null)
            }}
          />
        )}
      </div>
    </PhoneFrame>
  )
}

export default App
