import { ChevronLeft, ChevronRight, Loader2 } from 'lucide-react'
import type { PDFDocumentProxy } from 'pdfjs-dist'
import { useCallback, useEffect, useRef, useState } from 'react'
import { Document, Page, pdfjs } from 'react-pdf'
import 'react-pdf/dist/Page/TextLayer.css'
import type { Citation } from '../../lib/types'
import { useCitedText } from '../../lib/useCitedText'

pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  'pdfjs-dist/build/pdf.worker.min.mjs',
  import.meta.url,
).toString()

export function PdfView({ citation }: { citation: Citation }) {
  const docId = citation.document_id as string
  const page = typeof citation.location.page === 'number' ? citation.location.page : undefined
  const citedText = useCitedText(citation)
  const probe = citedText.replace(/\s+/g, ' ').toLowerCase()

  const wrapRef = useRef<HTMLDivElement>(null)
  const [width, setWidth] = useState(0)
  const [numPages, setNumPages] = useState(0)
  const [current, setCurrent] = useState(page && page > 0 ? page : 1)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const el = wrapRef.current
    if (!el) return
    const update = () => setWidth(el.clientWidth - 32)
    update()
    const ro = new ResizeObserver(update)
    ro.observe(el)
    return () => ro.disconnect()
  }, [])

  // Highlight only text fragments that belong to the cited passage (no scatter).
  const textRenderer = useCallback(
    (item: { str: string }) => {
      const s = item.str.trim().toLowerCase()
      return s.length > 3 && probe.includes(s) ? `<mark>${item.str}</mark>` : item.str
    },
    [probe],
  )

  function onLoad(pdf: PDFDocumentProxy) {
    setNumPages(pdf.numPages)
    setCurrent((c) => Math.min(Math.max(c, 1), pdf.numPages))
  }

  return (
    <div ref={wrapRef} className="flex h-full flex-col">
      <div className="flex-1 overflow-auto p-4">
        {error ? (
          <p className="text-sm text-red-500">{error}</p>
        ) : (
          <Document
            file={`/documents/${docId}/file`}
            onLoadSuccess={onLoad}
            onLoadError={(e) => setError(e.message)}
            loading={<Loading />}
            error={<p className="text-sm text-red-500">Gagal memuat PDF.</p>}
          >
            {width > 0 && (
              <Page
                pageNumber={current}
                width={width}
                customTextRenderer={textRenderer}
                renderAnnotationLayer={false}
              />
            )}
          </Document>
        )}
      </div>
      {numPages > 0 && (
        <div className="flex shrink-0 items-center justify-center gap-4 border-t border-border py-2 text-xs">
          <button
            onClick={() => setCurrent((c) => Math.max(1, c - 1))}
            disabled={current <= 1}
            aria-label="Halaman sebelumnya"
            className="cursor-pointer rounded p-1 text-muted hover:text-fg disabled:opacity-40"
          >
            <ChevronLeft className="h-4 w-4" />
          </button>
          <span className="text-muted">
            Hal. {current} / {numPages}
          </span>
          <button
            onClick={() => setCurrent((c) => Math.min(numPages, c + 1))}
            disabled={current >= numPages}
            aria-label="Halaman berikutnya"
            className="cursor-pointer rounded p-1 text-muted hover:text-fg disabled:opacity-40"
          >
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      )}
    </div>
  )
}

function Loading() {
  return (
    <div className="flex items-center gap-2 text-sm text-muted">
      <Loader2 className="h-4 w-4 animate-spin" /> Memuat…
    </div>
  )
}
