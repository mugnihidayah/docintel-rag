import { ChevronDown, Loader2 } from 'lucide-react'
import { useState } from 'react'
import type { ChatMessage, Citation } from '../lib/types'
import { CitationCard } from './CitationCard'

export function MessageBubble({
  message,
  onCite,
}: {
  message: ChatMessage
  onCite: (citation: Citation) => void
}) {
  const [showSources, setShowSources] = useState(false)

  if (message.role === 'user') {
    return (
      <div className="flex justify-end">
        <div className="max-w-[80%] rounded-2xl rounded-br-sm bg-primary px-4 py-2.5 text-sm text-white">
          {message.text}
        </div>
      </div>
    )
  }

  if (message.pending) {
    return (
      <div className="flex items-center gap-2 text-sm text-muted">
        <Loader2 className="h-4 w-4 animate-spin" />
        Mencari &amp; merangkai jawaban…
      </div>
    )
  }

  const result = message.result

  return (
    <div className="space-y-3">
      <div
        className={`max-w-[85%] rounded-2xl rounded-bl-sm px-4 py-3 text-sm leading-relaxed ${
          message.error
            ? 'bg-red-500/10 text-red-600 dark:text-red-400'
            : 'border border-border bg-surface'
        }`}
      >
        {message.text}
      </div>

      {result && result.citations.length > 0 && (
        <div className="space-y-2">
          <button
            onClick={() => setShowSources((s) => !s)}
            aria-expanded={showSources}
            className="flex cursor-pointer items-center gap-1 text-xs font-semibold uppercase tracking-wide text-muted transition-colors hover:text-fg"
          >
            <ChevronDown
              className={`h-3.5 w-3.5 transition-transform ${showSources ? '' : '-rotate-90'}`}
            />
            {showSources ? 'Sembunyikan' : 'Lihat'} sumber ({result.citations.length})
          </button>

          {showSources && (
            <>
              <div className="grid gap-2">
                {result.citations.map((c, i) => (
                  <CitationCard key={i} index={i + 1} citation={c} onOpen={() => onCite(c)} />
                ))}
              </div>
              <p className="pt-1 text-[11px] text-muted">
                {result.model} · {result.latency_ms} ms · {result.retrieved_chunks} chunk
              </p>
            </>
          )}
        </div>
      )}
    </div>
  )
}
