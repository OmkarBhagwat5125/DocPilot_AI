# DocPilot AI — UI/UX Design Specification
**Version 2.0 — Bright, Minimalist, Chatbot-First Redesign**

> This document replaces all previous DocPilot AI design structure. It defines a fresh visual system inspired by the current generation of production chatbots (ChatGPT, Claude, Gemini, Perplexity) and introduces a new **View Document** panel alongside the chat.

---

## 1. Design Philosophy

DocPilot AI is a multi-tenant, multi-format RAG document intelligence platform. The redesign treats it as a **chatbot-first product**: the conversation is the primary surface, and the document is a supporting panel the user can summon on demand — the same pattern ChatGPT's Canvas, Claude's Artifacts, and Perplexity's source panel all converged on in 2025–2026.

Core principles:
1. **Bright over dark** — a light, airy base theme (most competitors default to dark panels; a bright theme differentiates DocPilot and reads as "clarity for your documents").
2. **Minimalist, not empty** — generous whitespace, a centered chat column, one clear action at a time — but "rich" through purposeful detail: citation chips, streaming cursors, subtle motion, and a live document preview.
3. **Trust through transparency** — every AI answer shows *where it came from*. Source citations are first-class UI, not a footnote.
4. **One conversation, two surfaces** — Chat (left/center) + View Document (right), so the user never loses context switching between "asking" and "reading."

---

## 2. Reference Benchmarks (2026)

| Pattern | Seen in | Applied in DocPilot as |
|---|---|---|
| Streaming text with visible cursor | ChatGPT, Claude, Gemini, Perplexity | Default for every AI response |
| Inline source citation chips | Perplexity | Numbered chips `[1] [2]` under each answer, linked to the View Document panel |
| Centered chat column, persistent bottom input bar | ChatGPT | Main chat layout |
| Side canvas / artifact panel | ChatGPT Canvas, Claude Artifacts | **View Document** panel |
| Subtle glassmorphism for AI-generated layers | ChatGPT, Claude, Gemini | Answer cards, citation panel header |
| Behavioral mode labels instead of technical ones | ChatGPT ("Auto/Fast/Thinking") | DocPilot modes: **Quick Answer** / **Deep Search** |

---

## 3. Color System (Bright Theme)

```
--bg-base:        #FCFCFA   /* warm off-white canvas */
--bg-surface:      #FFFFFF   /* cards, panels */
--bg-subtle:        #F3F4F8   /* input bar, hover states */

--brand-primary:  #4F46E5   /* indigo — primary actions, links */
--brand-accent:    #06B6D4   /* cyan — highlights, active states */
--brand-gradient:  linear-gradient(135deg, #6366F1 0%, #06B6D4 100%)

--text-primary:    #14151A
--text-secondary: #5B5F6B
--text-muted:      #9AA0AC

--success:          #16A34A
--warning:         #F59E0B
--danger:            #DC2626

--border-subtle:  #E7E8EE
--border-focus:    #6366F1

--citation-chip:  #EEF2FF   /* bg */  /  #4F46E5 /* text */
```

Accent gradient (`--brand-gradient`) is reserved for: the send button, the DocPilot logo mark, and the streaming-cursor glow — used sparingly so it stays a signature, not wallpaper.

---

## 4. Typography

- **Primary font:** Inter (UI text, chat body)
- **Monospace:** JetBrains Mono (code blocks, extracted table data)
- **Scale:**
  - Display / empty-state greeting: 28px / 600
  - Chat message: 15px / 400, line-height 1.6
  - Citation chip: 12px / 600, uppercase tracking
  - Sidebar labels: 13px / 500

---

## 5. Layout Structure

```
┌──────────────┬───────────────────────────────┬───────────────────────┐
│   Sidebar    │           Chat Column           │   View Document       │
│   (240px)    │           (flex, centered)      │   Panel (420px,       │
│              │                                  │   collapsible)        │
│  + New Chat  │  ┌───────────────────────────┐  │  ┌──────────────────┐ │
│  Documents   │  │ "What's in this contract?" │  │  │  contract.pdf     │ │
│  Recent      │  └───────────────────────────┘  │  │  ──────────────── │ │
│  chats       │  ┌───────────────────────────┐  │  │  page 4 highlighted│ │
│  Workspace   │  │ AI answer, streaming...     │  │  │  (jump-to-source) │ │
│  switcher    │  │ [1] [2]  ← citation chips   │  │  │                    │ │
│              │  └───────────────────────────┘  │  │  [Download] [Open] │ │
│              │  ────────── input bar ────────  │  └──────────────────┘ │
└──────────────┴───────────────────────────────┴───────────────────────┘
```

- **Sidebar:** workspace/tenant switcher (multi-tenant), document library, recent conversations, collapses to icon rail on mobile.
- **Chat Column:** centered, max-width 720px, bottom-anchored input bar with mode toggle (**Quick Answer** / **Deep Search**), attach button, mic icon.
- **View Document Panel (new):** opens automatically when a citation chip is clicked, or manually via a "View Doc" button on any AI message. Shows the source file rendered inline (PDF/DOCX/TXT/image preview) with the cited passage auto-highlighted and scrolled into view. Includes Download and "Open in new tab" actions. Collapsible to give the chat full width.

---

## 6. Core Components

### 6.1 Chat Message Card
- User messages: right-aligned, `--bg-subtle` pill, no avatar.
- AI messages: left-aligned, `--bg-surface` card, soft 1px `--border-subtle`, subtle shadow (`0 1px 3px rgba(20,21,26,0.06)`).
- Streaming state: animated cursor with a faint gradient glow (`--brand-gradient` at 15% opacity).
- Footer row: citation chips, copy button, regenerate button, "View Doc" pill button.

### 6.2 Citation Chip
- Small rounded pill, `--citation-chip` background.
- Hover: lifts slightly, shows filename + page/section tooltip.
- Click: opens **View Document** panel scrolled to that exact passage, passage highlighted in `--brand-accent` at 20% opacity.

### 6.3 View Document Panel (New Feature)
- Header: filename, file-type icon, close (✕) and collapse (⤢) controls.
- Body: native inline renderer —
  - PDF → page-by-page canvas render with highlight overlay
  - DOCX → converted HTML preview
  - TXT/CSV → syntax-aware plain view
  - Image-based docs → OCR text overlay toggle
- Footer: `Download original`, `Open in new tab`, `Ask about this page` (re-focuses chat input pre-filled with page context).
- Empty state (no doc selected): a soft illustration + "Click any citation to preview its source here."

### 6.4 Input Bar
- Rounded 16px, `--bg-subtle` fill, floats above page bottom with 24px margin.
- Left: attach/upload icon (multi-format).
- Center: text field, placeholder rotates through example prompts.
- Right: mode toggle chip (Quick Answer / Deep Search) + gradient send button.

### 6.5 Empty State / Landing
- Centered DocPilot wordmark with gradient icon mark.
- Greeting: "What would you like to know from your documents?"
- Four suggestion cards (bright, soft-shadow tiles) with example prompts, replacing the old plain link list.

---

## 7. Motion & Micro-interactions

- Message entrance: fade + 6px slide-up, 180ms ease-out.
- Citation chip hover: 4px lift, 120ms.
- View Document panel open/close: slide from right, 240ms cubic-bezier(0.4,0,0.2,1).
- Streaming cursor: 1s pulse loop on the gradient glow.
- Send button: brief scale-down (0.95) on click for tactile feedback.

---

## 8. Accessibility

- Minimum contrast ratio 4.5:1 for all body text against `--bg-base`/`--bg-surface`.
- Citation chips and mode toggles fully keyboard-navigable, visible focus ring in `--border-focus`.
- View Document panel reachable via keyboard shortcut (`Ctrl/Cmd + D`) and screen-reader labeled as a complementary landmark.
- Respects `prefers-reduced-motion` — disables slide/pulse animations, keeps instant state changes.

---

## 9. What Changed From the Previous Structure

| Old | New |
|---|---|
| Dense, utilitarian dashboard layout | Centered, chatbot-first conversational layout |
| Dark/neutral theme | Bright, warm off-white theme with indigo–cyan gradient accent |
| Sources listed as plain text/links | Interactive citation chips tied to a live document view |
| No in-app document preview | New **View Document** panel with highlight-on-citation |
| Static send button | Streaming responses with animated cursor, mode toggle (Quick Answer / Deep Search) |
| Generic empty state | Guided empty state with prompt suggestion cards |

---

## 10. Implementation Notes (for React + Tailwind build)

- Use CSS variables above as Tailwind theme extensions (`theme.extend.colors`).
- View Document panel should be a resizable/collapsible flex sibling, not a modal — keeps chat scroll position intact.
- PDF rendering: `pdf.js` canvas layer + an absolutely-positioned highlight `<div>` synced to citation bounding-box coordinates returned by the RAG backend.
- Persist panel width and last-viewed document per session in local component state (not localStorage, per multi-tenant isolation).
