import { Loader2 } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import * as XLSX from 'xlsx'
import type { Citation } from '../../lib/types'

interface SheetData {
  sheet: string
  rows: string[][]
}

export function SheetView({ citation }: { citation: Citation }) {
  const docId = citation.document_id as string
  const location = citation.location
  const [data, setData] = useState<SheetData | null>(null)
  const [error, setError] = useState<string | null>(null)
  const targetRef = useRef<HTMLTableRowElement>(null)

  useEffect(() => {
    let active = true
    fetch(`/documents/${docId}/file`)
      .then((r) => r.arrayBuffer())
      .then((buf) => {
        const wb = XLSX.read(buf, { type: 'array' })
        const wanted = String(location.sheet ?? '')
        const sheet = wb.SheetNames.includes(wanted) ? wanted : wb.SheetNames[0]
        const rows = XLSX.utils.sheet_to_json(wb.Sheets[sheet], {
          header: 1,
          raw: false,
          blankrows: false,
        }) as string[][]
        if (active) setData({ sheet, rows })
      })
      .catch((e: Error) => {
        if (active) setError(e.message)
      })
    return () => {
      active = false
    }
  }, [docId, location])

  useEffect(() => {
    if (data) targetRef.current?.scrollIntoView({ block: 'center' })
  }, [data])

  if (error) return <p className="p-6 text-sm text-red-500">{error}</p>
  if (!data) {
    return (
      <div className="flex items-center gap-2 p-6 text-sm text-muted">
        <Loader2 className="h-4 w-4 animate-spin" /> Memuat sheet…
      </div>
    )
  }

  const start = Number(location.row_start ?? 0)
  const end = Number(location.row_end ?? start)

  return (
    <div className="h-full overflow-auto p-4">
      <p className="mb-2 text-xs font-medium text-muted">Sheet: {data.sheet}</p>
      <table className="border-collapse text-xs">
        <tbody>
          {data.rows.map((row, i) => {
            const lineNo = i + 1
            const cited = start > 0 && lineNo >= start && lineNo <= end
            return (
              <tr
                key={i}
                ref={cited ? targetRef : undefined}
                className={cited ? 'source-highlight' : undefined}
              >
                <td className="border border-border px-2 py-1 text-right text-muted">{lineNo}</td>
                {row.map((cell, j) => (
                  <td key={j} className="border border-border px-2 py-1 whitespace-nowrap">
                    {cell}
                  </td>
                ))}
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
