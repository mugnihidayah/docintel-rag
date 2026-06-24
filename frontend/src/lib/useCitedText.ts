import { useEffect, useState } from 'react'
import { getDocumentChunks } from './api'
import type { Citation } from './types'

function isCited(
  target: Record<string, string | number>,
  chunk: Record<string, string | number>,
): boolean {
  const keys = Object.keys(target)
  return keys.length > 0 && keys.every((k) => String(target[k]) === String(chunk[k]))
}

// Resolve the full text of the cited chunk (by location) for accurate highlighting.
// Falls back to the (truncated) citation snippet until the chunk is loaded.
export function useCitedText(citation: Citation): string {
  const [text, setText] = useState(citation.snippet)

  useEffect(() => {
    let active = true
    setText(citation.snippet)
    if (!citation.document_id) return
    getDocumentChunks(citation.document_id)
      .then((d) => {
        const match = d.chunks.find((c) => isCited(citation.location, c.location))
        if (active && match) setText(match.text)
      })
      .catch(() => {
        /* keep snippet fallback */
      })
    return () => {
      active = false
    }
  }, [citation])

  return text
}
