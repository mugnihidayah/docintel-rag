import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// Dev server proxies API calls to the FastAPI backend on :8000.
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '/documents': 'http://localhost:8000',
      '/query': 'http://localhost:8000',
      '/health': 'http://localhost:8000',
    },
  },
})
