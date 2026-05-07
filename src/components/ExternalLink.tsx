interface ExternalLinkProps {
  href: string
  label?: string
  className?: string
}

export function ExternalLink({ href, label = 'Open original', className }: ExternalLinkProps) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      onClick={(e) => e.stopPropagation()}
      title={label}
      aria-label={label}
      className={
        'inline-flex items-center gap-1 rounded-full border border-slate-200 bg-white px-2 py-0.5 text-[10px] font-semibold text-slate-600 shadow-sm hover:border-blue-300 hover:text-blue-600 ' +
        (className ?? '')
      }
    >
      <span>Open</span>
      <svg
        className="h-3 w-3"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        viewBox="0 0 24 24"
        aria-hidden
      >
        <path strokeLinecap="round" strokeLinejoin="round" d="M14 4h6v6" />
        <path strokeLinecap="round" strokeLinejoin="round" d="M10 14 20 4" />
        <path strokeLinecap="round" strokeLinejoin="round" d="M19 13v5a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h5" />
      </svg>
    </a>
  )
}
