import { useCallback, useEffect, useState } from 'react'
import { Chat } from './components/Chat'
import { Sidebar } from './components/Sidebar'
import { SourceViewer } from './components/SourceViewer'
import { ThemeToggle } from './components/ThemeToggle'
import { deleteDocument, listDocuments, queryDocs, uploadDocument } from './lib/api'
import type { ChatMessage, Citation, DocumentOut } from './lib/types'

export default function App() {
  const [documents, setDocuments] = useState<DocumentOut[]>([])
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [asking, setAsking] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [docError, setDocError] = useState<string | null>(null)
  const [viewing, setViewing] = useState<Citation | null>(null)

  const refreshDocs = useCallback(async () => {
    try {
      setDocuments(await listDocuments())
      setDocError(null)
    } catch (e) {
      setDocError((e as Error).message)
    }
  }, [])

  useEffect(() => {
    void refreshDocs()
  }, [refreshDocs])

  const handleUpload = async (file: File) => {
    setUploading(true)
    setDocError(null)
    try {
      await uploadDocument(file)
      await refreshDocs()
    } catch (e) {
      setDocError((e as Error).message)
    } finally {
      setUploading(false)
    }
  }

  const handleDelete = async (id: string) => {
    try {
      await deleteDocument(id)
      await refreshDocs()
    } catch (e) {
      setDocError((e as Error).message)
    }
  }

  const handleAsk = async (question: string) => {
    const pendingId = crypto.randomUUID()
    setMessages((m) => [
      ...m,
      { id: crypto.randomUUID(), role: 'user', text: question },
      { id: pendingId, role: 'assistant', text: '', pending: true },
    ])
    setAsking(true)
    try {
      const result = await queryDocs(question)
      setMessages((m) =>
        m.map((msg) =>
          msg.id === pendingId ? { ...msg, text: result.answer, result, pending: false } : msg,
        ),
      )
    } catch (e) {
      setMessages((m) =>
        m.map((msg) =>
          msg.id === pendingId
            ? { ...msg, text: (e as Error).message, error: true, pending: false }
            : msg,
        ),
      )
    } finally {
      setAsking(false)
    }
  }

  return (
    <div className="flex h-screen overflow-hidden bg-bg font-sans text-fg">
      <Sidebar
        documents={documents}
        uploading={uploading}
        error={docError}
        onUpload={handleUpload}
        onDelete={handleDelete}
        onRefresh={refreshDocs}
      />
      <main className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-14 items-center justify-between border-b border-border px-6">
          <div>
            <h1 className="text-sm font-semibold">Tanya Dokumen</h1>
            <p className="text-xs text-muted">Jawaban grounded + sitasi yang bisa ditrace</p>
          </div>
          <ThemeToggle />
        </header>
        <Chat
          messages={messages}
          asking={asking}
          hasDocs={documents.length > 0}
          onAsk={handleAsk}
          onCite={setViewing}
        />
      </main>
      {viewing && <SourceViewer citation={viewing} onClose={() => setViewing(null)} />}
    </div>
  )
}
