import type { DocStatus } from '../lib/types'

const STYLES: Record<DocStatus, string> = {
  indexed: 'bg-green-500/15 text-green-600 dark:text-green-400',
  indexing: 'bg-amber-500/15 text-amber-600 dark:text-amber-400',
  pending: 'bg-slate-500/15 text-slate-500 dark:text-slate-400',
  failed: 'bg-red-500/15 text-red-600 dark:text-red-400',
}

const LABELS: Record<DocStatus, string> = {
  indexed: 'terindeks',
  indexing: 'mengindeks',
  pending: 'menunggu',
  failed: 'gagal',
}

export function StatusBadge({ status }: { status: DocStatus }) {
  return (
    <span className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${STYLES[status]}`}>
      {LABELS[status]}
    </span>
  )
}
