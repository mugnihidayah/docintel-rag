import { AlertCircle, FileText, Loader2, Plus, RefreshCw, Trash2 } from 'lucide-react'
import type { ChangeEvent } from 'react'
import { useRef } from 'react'
import type { DocumentOut } from '../lib/types'
import { StatusBadge } from './StatusBadge'

interface Props {
  documents: DocumentOut[]
  uploading: boolean
  error: string | null
  onUpload: (file: File) => void
  onDelete: (id: string) => void
  onRefresh: () => void
}

export function Sidebar({ documents, uploading, error, onUpload, onDelete, onRefresh }: Props) {
  const inputRef = useRef<HTMLInputElement>(null)

  const onChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) onUpload(file)
    e.target.value = ''
  }

  return (
    <aside className="flex w-72 shrink-0 flex-col border-r border-border bg-surface">
      <div className="flex h-14 items-center gap-2 border-b border-border px-5">
        <div className="grid h-8 w-8 place-items-center rounded-lg bg-primary text-white">
          <FileText className="h-4 w-4" />
        </div>
        <span className="font-bold tracking-tight">DocIntel</span>
      </div>

      <div className="p-4">
        <button
          onClick={() => inputRef.current?.click()}
          disabled={uploading}
          className="flex w-full cursor-pointer items-center justify-center gap-2 rounded-lg bg-primary px-3 py-2 text-sm font-medium text-white transition-colors hover:bg-primary-hover disabled:cursor-not-allowed disabled:opacity-60"
        >
          {uploading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Plus className="h-4 w-4" />}
          {uploading ? 'Mengindeks…' : 'Upload dokumen'}
        </button>
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx,.pptx,.xlsx,.csv,.txt"
          className="hidden"
          onChange={onChange}
        />
      </div>

      <div className="flex items-center justify-between px-5 pb-2">
        <span className="text-xs font-semibold uppercase tracking-wide text-muted">
          Dokumen ({documents.length})
        </span>
        <button
          onClick={onRefresh}
          aria-label="Muat ulang daftar dokumen"
          className="cursor-pointer rounded p-1 text-muted transition-colors hover:text-fg"
        >
          <RefreshCw className="h-3.5 w-3.5" />
        </button>
      </div>

      {error && (
        <div className="mx-4 mb-2 flex items-start gap-2 rounded-lg bg-red-500/10 p-2 text-xs text-red-600 dark:text-red-400">
          <AlertCircle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <div className="flex-1 overflow-y-auto px-3 pb-4">
        {documents.length === 0 ? (
          <p className="px-2 py-8 text-center text-xs text-muted">
            Belum ada dokumen. Upload PDF, DOCX, PPTX, XLSX, atau CSV untuk mulai bertanya.
          </p>
        ) : (
          <ul className="space-y-1">
            {documents.map((doc) => (
              <li
                key={doc.id}
                className="group flex items-center gap-2 rounded-lg px-2 py-2 transition-colors hover:bg-bg"
              >
                <FileText className="h-4 w-4 shrink-0 text-muted" />
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm" title={doc.filename}>
                    {doc.filename}
                  </p>
                  <div className="mt-0.5 flex items-center gap-1.5">
                    <StatusBadge status={doc.status} />
                    <span className="text-[11px] text-muted">{doc.num_chunks} chunk</span>
                  </div>
                </div>
                <button
                  onClick={() => onDelete(doc.id)}
                  aria-label={`Hapus ${doc.filename}`}
                  className="cursor-pointer rounded p-1 text-muted opacity-0 transition-all hover:text-red-500 group-hover:opacity-100"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </aside>
  )
}
