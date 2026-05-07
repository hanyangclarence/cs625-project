interface SearchBarProps {
  query: string
  onQueryChange: (next: string) => void
  exampleLabel: string
  onOpenOptions: () => void
  onSubmit?: (query: string) => void
  submitDisabled?: boolean
}

export function SearchBar({
  query,
  onQueryChange,
  exampleLabel,
  onOpenOptions,
  onSubmit,
  submitDisabled,
}: SearchBarProps) {
  function trySubmit() {
    const trimmed = query.trim()
    if (!trimmed || !onSubmit || submitDisabled) return
    onSubmit(trimmed)
  }

  return (
    <div className="px-4 pt-3 pb-2">
      <div className="mb-2 flex items-center justify-between">
        <div>
          <p className="text-[11px] uppercase tracking-widest text-slate-400">Topic</p>
          <p className="truncate text-xs text-slate-500">{exampleLabel}</p>
        </div>
        <button
          type="button"
          onClick={onOpenOptions}
          className="rounded-full border border-slate-200 bg-white px-3 py-1 text-[11px] font-semibold text-slate-600 shadow-sm active:scale-[0.98]"
        >
          View options
        </button>
      </div>
      <form
        onSubmit={(e) => {
          e.preventDefault()
          trySubmit()
        }}
        className="flex items-center gap-2 rounded-2xl border border-slate-200 bg-white px-3 py-2 shadow-sm"
      >
        <svg
          className="h-4 w-4 text-slate-400"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          viewBox="0 0 24 24"
        >
          <circle cx="11" cy="11" r="7" />
          <path strokeLinecap="round" d="m20 20-3.5-3.5" />
        </svg>
        <input
          value={query}
          onChange={(e) => onQueryChange(e.target.value)}
          placeholder="Type a topic + Enter, or filter the loaded one"
          className="w-full bg-transparent text-sm text-slate-700 placeholder:text-slate-400 focus:outline-none"
        />
        {query && (
          <button
            type="button"
            onClick={() => onQueryChange('')}
            aria-label="Clear search"
            className="rounded-full px-1 text-slate-400 hover:text-slate-600"
          >
            ×
          </button>
        )}
        {onSubmit && (
          <button
            type="submit"
            disabled={!query.trim() || !!submitDisabled}
            className="rounded-full bg-blue-600 px-3 py-1 text-[11px] font-semibold text-white shadow-sm transition-opacity disabled:cursor-not-allowed disabled:opacity-40"
          >
            Run
          </button>
        )}
      </form>
    </div>
  )
}
