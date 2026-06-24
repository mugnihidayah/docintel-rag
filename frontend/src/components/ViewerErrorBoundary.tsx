import { Component, type ReactNode } from 'react'

interface Props {
  children: ReactNode
}

interface State {
  error: string | null
}

// Keeps a crash in one source viewer from blanking the whole panel; shows the message.
export class ViewerErrorBoundary extends Component<Props, State> {
  state: State = { error: null }

  static getDerivedStateFromError(error: Error): State {
    return { error: error.message }
  }

  render(): ReactNode {
    if (this.state.error) {
      return (
        <div className="p-6 text-sm text-red-500">
          Gagal menampilkan dokumen: {this.state.error}
        </div>
      )
    }
    return this.props.children
  }
}
