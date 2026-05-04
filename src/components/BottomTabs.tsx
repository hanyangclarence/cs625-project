export type ViewKey = 'cross-source' | 'evidence' | 'timeline'

interface BottomTabsProps {
  active: ViewKey
  onChange: (next: ViewKey) => void
}

const tabs: { key: ViewKey; label: string; icon: string }[] = [
  { key: 'cross-source', label: 'Cross-Source', icon: '⇌' },
  { key: 'evidence', label: 'Evidence Trace', icon: '◎' },
  { key: 'timeline', label: 'Claim Timeline', icon: '⧗' },
]

export function BottomTabs({ active, onChange }: BottomTabsProps) {
  return (
    <nav className="border-t border-slate-200 bg-white/95 backdrop-blur px-2 py-2">
      <div className="grid grid-cols-3 gap-1">
        {tabs.map((t) => {
          const isActive = t.key === active
          return (
            <button
              key={t.key}
              type="button"
              onClick={() => onChange(t.key)}
              aria-pressed={isActive}
              className={
                'flex flex-col items-center gap-0.5 rounded-xl py-1.5 text-[11px] font-medium transition-colors ' +
                (isActive
                  ? 'bg-blue-50 text-blue-600'
                  : 'text-slate-500 hover:text-slate-700')
              }
            >
              <span className="text-base leading-none">{t.icon}</span>
              {t.label}
            </button>
          )
        })}
      </div>
    </nav>
  )
}
