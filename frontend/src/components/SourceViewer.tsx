import { AlertCircle, FileText, Loader2, X } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import { getDocumentChunks } from '../lib/api'
import type { Citation, DocumentChunk } from '../lib/types'

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
  return ''
}

// A chunk is the cited one when every key of the citation location matches.
function isCited(
  target: Record<string, string | number>,
  chunk: Record<string, string | number>,
): boolean {
  const keys = Object.keys(target)
  if (keys.length === 0) return false
  return keys.every((k) => String(target[k]) === String(chunk[k]))
}

export function SourceViewer({ citation, onClose }: { citation: Citation; onClose: () => void }) {
  const [chunks, setChunks] = useState<DocumentChunk[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const targetRef = useRef<HTMLParagraphElement>(null)

  useEffect(() => {
    let active = true
    setChunks(null)
    setError(null)
    if (!citation.document_id) {
      setError('Dokumen sumber tidak tersedia')
      return
    }
    getDocumentChunks(citation.document_id)
      .then((d) => {
        if (active) setChunks(d.chunks)
      })
      .catch((e: Error) => {
        if (active) setError(e.message)
      })
    return () => {
      active = false
    }
  }, [citation])

  useEffect(() => {
    if (!chunks) return
    const t = setTimeout(
      () => targetRef.current?.scrollIntoView({ block: 'center', behavior: 'smooth' }),
      60,
    )
    return () => clearTimeout(t)
  }, [chunks])

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  return (
    <div
      className="fixed inset-0 z-50 flex justify-end bg-black/40 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="flex h-full w-full max-w-xl flex-col bg-surface shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <header className="flex h-14 shrink-0 items-center gap-2 border-b border-border px-5">
          <FileText className="h-4 w-4 shrink-0 text-primary" />
          <span className="truncate text-sm font-semibold" title={citation.filename ?? ''}>
            {citation.filename ?? 'Dokumen'}
          </span>
          <span className="shrink-0 rounded bg-primary/10 px-1.5 py-0.5 text-[10px] font-medium text-primary">
            {formatLocation(citation.location)}
          </span>
          <button
            onClick={onClose}
            aria-label="Tutup"
            className="ml-auto cursor-pointer rounded p-1 text-muted transition-colors hover:text-fg"
          >
            <X className="h-4 w-4" />
          </button>
        </header>

        <div className="flex-1 overflow-y-auto px-6 py-5">
          {error ? (
            <div className="flex items-start gap-2 rounded-lg bg-red-500/10 p-3 text-sm text-red-600 dark:text-red-400">
              <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
              <span>{error}</span>
            </div>
          ) : !chunks ? (
            <div className="flex items-center gap-2 text-sm text-muted">
              <Loader2 className="h-4 w-4 animate-spin" />
              Memuat dokumen…
            </div>
          ) : chunks.length === 0 ? (
            <p className="text-sm text-muted">Tidak ada konten untuk ditampilkan.</p>
          ) : (
            <div className="space-y-1.5">
              {chunks.map((c, i) => {
                const cited = isCited(citation.location, c.location)
                return (
                  <p
                    key={i}
                    ref={cited ? targetRef : undefined}
                    className={
                      cited
                        ? 'scroll-mt-6 rounded-md bg-amber-200/60 px-2 py-1.5 text-sm leading-relaxed text-fg ring-1 ring-amber-400/60 dark:bg-amber-400/15'
                        : 'px-2 py-1 text-sm leading-relaxed text-muted'
                    }
                  >
                    {c.text}
                  </p>
                )
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
