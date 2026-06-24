import { Send, Sparkles } from 'lucide-react'
import type { FormEvent, KeyboardEvent } from 'react'
import { useEffect, useRef, useState } from 'react'
import type { ChatMessage, Citation } from '../lib/types'
import { MessageBubble } from './MessageBubble'

interface Props {
  messages: ChatMessage[]
  asking: boolean
  hasDocs: boolean
  onAsk: (question: string) => void
  onCite: (citation: Citation) => void
}

const SAMPLES = [
  'Apa saja format dokumen yang wajib didukung?',
  'Apa saja kriteria penilaiannya?',
  'Ringkas poin utama dokumen ini',
]

export function Chat({ messages, asking, hasDocs, onAsk, onCite }: Props) {
  const [input, setInput] = useState('')
  const endRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const submit = (e?: FormEvent) => {
    e?.preventDefault()
    const q = input.trim()
    if (!q || asking) return
    onAsk(q)
    setInput('')
  }

  const onKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      submit()
    }
  }

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div className="flex-1 overflow-y-auto">
        <div className="mx-auto max-w-3xl px-6 py-6">
          {messages.length === 0 ? (
            <EmptyState hasDocs={hasDocs} onPick={onAsk} />
          ) : (
            <div className="space-y-6">
              {messages.map((m) => (
                <MessageBubble key={m.id} message={m} onCite={onCite} />
              ))}
            </div>
          )}
          <div ref={endRef} />
        </div>
      </div>

      <div className="border-t border-border px-6 py-4">
        <form onSubmit={submit} className="mx-auto flex max-w-3xl items-end gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={onKeyDown}
            rows={1}
            placeholder={
              hasDocs
                ? 'Tanyakan sesuatu tentang dokumenmu…'
                : 'Upload dokumen dulu untuk mulai bertanya'
            }
            aria-label="Pertanyaan"
            className="max-h-40 min-h-11 flex-1 resize-none rounded-xl border border-border bg-surface px-4 py-3 text-sm outline-none transition-colors placeholder:text-muted focus:border-primary"
          />
          <button
            type="submit"
            disabled={asking || !input.trim()}
            aria-label="Kirim pertanyaan"
            className="grid h-11 w-11 shrink-0 cursor-pointer place-items-center rounded-xl bg-primary text-white transition-colors hover:bg-primary-hover disabled:cursor-not-allowed disabled:opacity-50"
          >
            <Send className="h-4 w-4" />
          </button>
        </form>
      </div>
    </div>
  )
}

function EmptyState({ hasDocs, onPick }: { hasDocs: boolean; onPick: (q: string) => void }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center">
      <div className="mb-4 grid h-14 w-14 place-items-center rounded-2xl bg-primary/10 text-primary">
        <Sparkles className="h-7 w-7" />
      </div>
      <h2 className="text-lg font-semibold">Tanya apa pun tentang dokumenmu</h2>
      <p className="mt-1 max-w-sm text-sm text-muted">
        Jawaban dirangkai hanya dari isi dokumen, lengkap dengan sitasi sumbernya (file + lokasi).
      </p>
      {hasDocs && (
        <div className="mt-6 flex flex-wrap justify-center gap-2">
          {SAMPLES.map((s) => (
            <button
              key={s}
              onClick={() => onPick(s)}
              className="cursor-pointer rounded-full border border-border bg-surface px-3 py-1.5 text-xs text-muted transition-colors hover:border-primary hover:text-primary"
            >
              {s}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
