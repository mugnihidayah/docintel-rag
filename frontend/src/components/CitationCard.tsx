import type { Citation } from '../lib/types'

function formatLocation(loc: Record<string, string | number>): string {
  if ('page' in loc) return `hal. ${loc.page}`
  if ('slide' in loc) return `slide ${loc.slide}`
  if ('sheet' in loc) return `sheet ${loc.sheet}`
  if ('row_start' in loc) {
    const end = loc.row_end
    return end && end !== loc.row_start ? `baris ${loc.row_start}–${end}` : `baris ${loc.row_start}`
  }
  if ('section' in loc) return String(loc.section)
  if ('block_index' in loc) return `blok ${loc.block_index}`
  return '—'
}

export function CitationCard({
  index,
  citation,
  onOpen,
}: {
  index: number
  citation: Citation
  onOpen: () => void
}) {
  return (
    <div
      role="button"
      tabIndex={0}
      onClick={onOpen}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault()
          onOpen()
        }
      }}
      title="Lihat di dokumen sumber"
      className="cursor-pointer rounded-lg border border-border bg-bg p-3 transition-colors hover:border-primary focus:border-primary focus:outline-none"
    >
      <div className="flex items-center gap-2">
        <span className="grid h-5 w-5 shrink-0 place-items-center rounded bg-primary/10 text-[11px] font-semibold text-primary">
          {index}
        </span>
        <span className="truncate text-xs font-medium" title={citation.filename ?? ''}>
          {citation.filename ?? 'Tidak diketahui'}
        </span>
        <span className="shrink-0 rounded bg-surface px-1.5 py-0.5 text-[10px] text-muted">
          {formatLocation(citation.location)}
        </span>
        {citation.score != null && (
          <span className="ml-auto shrink-0 text-[10px] text-muted">
            {citation.score.toFixed(2)} · {citation.score_type}
          </span>
        )}
      </div>
      <p className="mt-2 line-clamp-3 text-xs text-muted">{citation.snippet}</p>
    </div>
  )
}
