import type { ReactNode } from 'react'

interface PhoneFrameProps {
  statusDate: string
  windowLabel?: string
  children: ReactNode
}

export function PhoneFrame({ statusDate, windowLabel = 'WINDOW', children }: PhoneFrameProps) {
  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-slate-100 py-6 px-4">
      <div className="relative w-[390px] h-[844px] max-h-[calc(100vh-2rem)] bg-white rounded-[2.75rem] shadow-[0_30px_60px_-15px_rgba(15,23,42,0.35)] border border-slate-200 overflow-hidden flex flex-col">
        <div className="flex items-center justify-between px-6 pt-3 pb-2 text-[11px] font-semibold tracking-wide text-slate-500 bg-white">
          <span className="uppercase">AI News Comparison</span>
          <span>{statusDate}</span>
          <span className="flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
            {windowLabel}
          </span>
        </div>
        <div className="flex-1 overflow-y-auto">{children}</div>
      </div>
    </div>
  )
}
