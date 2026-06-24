export type DocStatus = 'pending' | 'indexing' | 'indexed' | 'failed'

export interface DocumentOut {
  id: string
  filename: string
  status: DocStatus
  num_chunks: number
  size_bytes: number
  created_at: string
}

export interface Citation {
  document_id: string | null
  filename: string | null
  location: Record<string, string | number>
  snippet: string
  score: number | null
  score_type: string
}

export interface QueryResult {
  answer: string
  citations: Citation[]
  retrieved_chunks: number
  model: string
  latency_ms: number
}

export interface DocumentChunk {
  text: string
  location: Record<string, string | number>
}

export interface DocumentChunks {
  document_id: string
  filename: string
  chunks: DocumentChunk[]
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  text: string
  result?: QueryResult
  pending?: boolean
  error?: boolean
}
