import { FileText, Loader2, X } from 'lucide-react'
import { lazy, Suspense, useEffect } from 'react'
import type { Citation } from '../lib/types'
import { ViewerErrorBoundary } from './ViewerErrorBoundary'
import { TextView } from './viewers/TextView'

// Heavy viewers (pdfjs / mammoth / xlsx) are code-split and loaded on demand.
const PdfView = lazy(() => import('./viewers/PdfView').then((m) => ({ default: m.PdfView })))
const DocxView = lazy(() => import('./viewers/DocxView').then((m) => ({ default: m.DocxView })))
const SheetView = lazy(() => import('./viewers/SheetView').then((m) => ({ default: m.SheetView })))

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

// Pick a renderer based on the file extension; fall back to the text view.
function ViewerBody({ citation }: { citation: Citation }) {
  if (!citation.document_id) {
    return <p className="p-6 text-sm text-muted">Dokumen sumber tidak tersedia.</p>
  }
  const ext = (citation.filename ?? '').split('.').pop()?.toLowerCase()
  switch (ext) {
    case 'pdf':
      return <PdfView citation={citation} />
    case 'docx':
      return <DocxView citation={citation} />
    case 'xlsx':
    case 'xls':
    case 'csv':
      return <SheetView citation={citation} />
    default:
      return <TextView citation={citation} />
  }
}

export function SourceViewer({ citation, onClose }: { citation: Citation; onClose: () => void }) {
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
        className="flex h-full w-full max-w-2xl flex-col bg-surface shadow-2xl"
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
        <div className="min-h-0 flex-1">
          <ViewerErrorBoundary key={`${citation.document_id}-${JSON.stringify(citation.location)}`}>
            <Suspense
              fallback={
                <div className="flex items-center gap-2 p-6 text-sm text-muted">
                  <Loader2 className="h-4 w-4 animate-spin" /> Memuat penampil…
                </div>
              }
            >
              <ViewerBody citation={citation} />
            </Suspense>
          </ViewerErrorBoundary>
        </div>
      </div>
    </div>
  )
}
