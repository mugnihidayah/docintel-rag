import type { DocumentChunks, DocumentOut, QueryResult } from './types'

// Optional API key (only needed when the backend enforces one, e.g. in deploy).
const API_KEY = import.meta.env.VITE_API_KEY

function authHeaders(): Record<string, string> {
  return API_KEY ? { 'X-API-Key': API_KEY } : {}
}

async function parse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = res.statusText
    try {
      const body = await res.json()
      detail = body?.error?.detail ?? detail
    } catch {
      /* response had no JSON body */
    }
    throw new Error(detail)
  }
  return res.json() as Promise<T>
}

export async function listDocuments(): Promise<DocumentOut[]> {
  return parse(await fetch('/documents'))
}

export async function uploadDocument(file: File): Promise<DocumentOut> {
  const form = new FormData()
  form.append('file', file)
  return parse(await fetch('/documents', { method: 'POST', headers: authHeaders(), body: form }))
}

export async function deleteDocument(id: string): Promise<void> {
  const res = await fetch(`/documents/${id}`, { method: 'DELETE', headers: authHeaders() })
  if (!res.ok) throw new Error('Gagal menghapus dokumen')
}

export async function queryDocs(question: string): Promise<QueryResult> {
  return parse(
    await fetch('/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
    }),
  )
}

export async function getDocumentChunks(id: string): Promise<DocumentChunks> {
  return parse(await fetch(`/documents/${id}/chunks`))
}
