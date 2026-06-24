# DocIntel — Frontend

React + Vite + TypeScript UI for the Document Intelligence System: upload documents, ask
questions, and get grounded answers with **traceable citations** — click a citation to open
the source document with the cited passage highlighted.

## Stack
- React 19 + TypeScript, Vite
- Tailwind CSS v4 (semantic tokens, light/dark theme toggle)
- lucide-react icons

## Prerequisites
The backend API must be running on `http://localhost:8000` (see `../backend`). The Vite dev
server proxies `/documents`, `/query`, and `/health` to it.

## Run
```bash
npm install
npm run dev        # http://localhost:5173
```

Other scripts:
```bash
npm run build      # type-check (tsc) + production build to dist/
npm run preview    # serve the production build
npm run lint       # oxlint
```

## Configuration
Copy `.env.example` to `.env.local` and set `VITE_API_KEY` **only** if the backend enforces
an API key (it is sent as `X-API-Key` on upload/delete). Not needed for local dev.

## Structure
```
src/
├─ App.tsx              app shell (sidebar + chat) + state
├─ index.css           Tailwind + light/dark design tokens
├─ lib/
│  ├─ api.ts            typed API client (documents, query, chunks)
│  ├─ types.ts          shared types
│  └─ useTheme.ts       light/dark toggle (persisted)
└─ components/
   ├─ Sidebar.tsx       document list + upload + status badges
   ├─ Chat.tsx          messages + composer + empty state
   ├─ MessageBubble.tsx answer bubble + collapsible citations
   ├─ CitationCard.tsx  clickable source card
   ├─ SourceViewer.tsx  document panel with highlighted cited passage
   ├─ StatusBadge.tsx   lifecycle status pill
   └─ ThemeToggle.tsx
```
