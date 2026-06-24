import { Loader2 } from 'lucide-react'
import { convertToHtml } from 'mammoth/mammoth.browser'
import { useEffect, useRef, useState } from 'react'
import { apiUrl } from '../../lib/api'
import type { Citation } from '../../lib/types'
import { useCitedText } from '../../lib/useCitedText'

// Highlight every rendered block that is part of the cited chunk's text, then scroll
// to the first one. Matching block-by-block keeps it accurate across headings + items.
function highlightSection(root: HTMLElement, citedText: string) {
  root.querySelectorAll('.source-highlight').forEach((e) => e.classList.remove('source-highlight'))
  const target = citedText.replace(/\s+/g, ' ').toLowerCase()
  if (target.length < 3) return

  const blocks = root.querySelectorAll<HTMLElement>('p, li, h1, h2, h3, h4, h5, td, th, blockquote')
  let first: HTMLElement | null = null
  for (const el of blocks) {
    const text = (el.textContent ?? '').replace(/\s+/g, ' ').trim().toLowerCase()
    if (text.length >= 3 && target.includes(text)) {
      el.classList.add('source-highlight')
      if (!first) first = el
    }
  }
  first?.scrollIntoView({ block: 'center' })
}

export function DocxView({ citation }: { citation: Citation }) {
  const docId = citation.document_id as string
  const citedText = useCitedText(citation)
  const [html, setHtml] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    let active = true
    fetch(apiUrl(`/documents/${docId}/file`))
      .then((r) => r.arrayBuffer())
      .then((buf) => convertToHtml({ arrayBuffer: buf }))
      .then((res) => {
        if (active) setHtml(res.value)
      })
      .catch((e: Error) => {
        if (active) setError(e.message)
      })
    return () => {
      active = false
    }
  }, [docId])

  useEffect(() => {
    if (!html || !ref.current) return
    const node = ref.current
    const t = setTimeout(() => highlightSection(node, citedText), 50)
    return () => clearTimeout(t)
  }, [html, citedText])

  if (error) return <p className="p-6 text-sm text-red-500">{error}</p>
  if (html === null) {
    return (
      <div className="flex items-center gap-2 p-6 text-sm text-muted">
        <Loader2 className="h-4 w-4 animate-spin" /> Memuat dokumen…
      </div>
    )
  }
  return (
    <div className="h-full overflow-auto p-6">
      <div ref={ref} className="docx-content" dangerouslySetInnerHTML={{ __html: html }} />
    </div>
  )
}
