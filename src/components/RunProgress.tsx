interface RunProgressProps {
  topic: string
  status: 'running' | 'error'
  progress: string[]
  error?: string | null
  onCancel: () => void
}

export function RunProgress({ topic, status, progress, error, onCancel }: RunProgressProps) {
  return (
    <div className="absolute inset-0 z-30 flex flex-col bg-white/95 backdrop-blur">
      <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
        <div>
          <p className="text-[10px] uppercase tracking-widest text-slate-400">
            {status === 'error' ? 'Run failed' : 'Building topic'}
          </p>
          <p className="truncate text-sm font-semibold text-slate-800">{topic}</p>
        </div>
        <button
          type="button"
          onClick={onCancel}
          className="rounded-full border border-slate-200 bg-white px-3 py-1 text-[11px] font-semibold text-slate-600 shadow-sm hover:border-slate-300"
        >
          {status === 'error' ? 'Close' : 'Hide'}
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-3">
        {status === 'running' && (
          <div className="mb-3 flex items-center gap-2 text-xs text-slate-500">
            <span className="inline-block h-2 w-2 animate-pulse rounded-full bg-blue-500" />
            <span>Pipeline running — this can take 1–6 minutes.</span>
          </div>
        )}
        {status === 'error' && error && (
          <div className="mb-3 rounded-xl border border-rose-200 bg-rose-50 p-3 text-xs text-rose-700">
            {error}
          </div>
        )}

        <ol className="space-y-1.5 font-mono text-[11px] leading-snug text-slate-600">
          {progress.length === 0 ? (
            <li className="text-slate-400">waiting for first event…</li>
          ) : (
            progress.map((line, i) => (
              <li
                key={i}
                className={
                  'rounded-md bg-slate-50 px-2 py-1 ' +
                  (line.startsWith('[done]') ? 'text-emerald-700 font-semibold' : '')
                }
              >
                {line}
              </li>
            ))
          )}
        </ol>
      </div>
    </div>
  )
}
