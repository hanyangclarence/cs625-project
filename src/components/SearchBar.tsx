interface SearchBarProps {
  query: string
  onQueryChange: (next: string) => void
  exampleLabel: string
  onOpenOptions: () => void
}

export function SearchBar({ query, onQueryChange, exampleLabel, onOpenOptions }: SearchBarProps) {
  return (
    <div className="px-4 pt-3 pb-2">
      <div className="mb-2 flex items-center justify-between">
        <div>
          <p className="text-[11px] uppercase tracking-widest text-slate-400">Selected example</p>
          <p className="text-xs text-slate-500">{exampleLabel}</p>
        </div>
        <button
          type="button"
          onClick={onOpenOptions}
          className="rounded-full border border-slate-200 bg-white px-3 py-1 text-[11px] font-semibold text-slate-600 shadow-sm active:scale-[0.98]"
        >
          View options
        </button>
      </div>
      <div className="flex items-center gap-2 rounded-2xl border border-slate-200 bg-white px-3 py-2 shadow-sm">
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
          placeholder="Example: Artemis II lunar flyby"
          className="w-full bg-transparent text-sm text-slate-700 placeholder:text-slate-400 focus:outline-none"
        />
      </div>
    </div>
  )
}
