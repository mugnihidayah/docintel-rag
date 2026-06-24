import { AlertCircle, Loader2 } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import { getDocumentChunks } from '../../lib/api'
import type { Citation, DocumentChunk } from '../../lib/types'

function isCited(
  target: Record<string, string | number>,
  chunk: Record<string, string | number>,
): boolean {
  const keys = Object.keys(target)
  if (keys.length === 0) return false
  return keys.every((k) => String(target[k]) === String(chunk[k]))
}

export function TextView({ citation }: { citation: Citation }) {
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

  if (error) {
    return (
      <div className="flex items-start gap-2 p-6 text-sm text-red-600 dark:text-red-400">
        <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
        <span>{error}</span>
      </div>
    )
  }
  if (!chunks) {
    return (
      <div className="flex items-center gap-2 p-6 text-sm text-muted">
        <Loader2 className="h-4 w-4 animate-spin" /> Memuat dokumen…
      </div>
    )
  }
  return (
    <div className="h-full space-y-1.5 overflow-auto px-6 py-5">
      {chunks.map((c, i) => {
        const cited = isCited(citation.location, c.location)
        return (
          <p
            key={i}
            ref={cited ? targetRef : undefined}
            className={
              cited
                ? 'source-highlight px-2 py-1.5 text-sm leading-relaxed text-fg'
                : 'px-2 py-1 text-sm leading-relaxed text-muted'
            }
          >
            {c.text}
          </p>
        )
      })}
    </div>
  )
}
