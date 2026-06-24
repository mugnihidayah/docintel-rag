import { Moon, Sun } from 'lucide-react'
import { useTheme } from '../lib/useTheme'

export function ThemeToggle() {
  const { theme, toggle } = useTheme()
  return (
    <button
      onClick={toggle}
      aria-label={theme === 'dark' ? 'Beralih ke mode terang' : 'Beralih ke mode gelap'}
      className="grid h-9 w-9 cursor-pointer place-items-center rounded-lg border border-border text-muted transition-colors hover:text-fg"
    >
      {theme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
    </button>
  )
}
