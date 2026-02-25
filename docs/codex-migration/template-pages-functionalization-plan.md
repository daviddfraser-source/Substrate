# Template Pages Functionalization Plan

## Scope Reviewed
- `templates/ai-substrate/app/kanban/page.tsx`
- `templates/ai-substrate/app/gantt/page.tsx`
- `templates/ai-substrate/app/timeline/page.tsx`
- `templates/ai-substrate/app/assistant/page.tsx`
- `templates/ai-substrate/app/chat/page.tsx`
- `templates/ai-substrate/app/knowledge/page.tsx`
- `templates/ai-substrate/app/documents/page.tsx`
- `templates/ai-substrate/app/approvals/page.tsx`
- `templates/ai-substrate/app/prompt-lab/page.tsx`
- `templates/ai-substrate/app/agent-console/page.tsx`
- `templates/ai-substrate/app/new/page.tsx`

## Current State
- Pages are currently placeholders (title + short description), except `/new` which contains a minimal form tied to `/api/items`.
- No shared template data model/patterns for these pages.
- No reusable starter interaction primitives (filters, detail drawers, mock workflows).

## Design Goals
- Every template route must be usable as a development jump-start, not a static placeholder.
- Each page must include realistic starter UX patterns: filtering, editing, status transitions, and detail context.
- Keep templates deterministic and local-first (no external service requirements by default).

## OSS Libraries Selected
- `@dnd-kit/core`, `@dnd-kit/sortable`, `@dnd-kit/utilities`:
  - Used for realistic drag-and-drop workflow template patterns in Kanban.
- `react-markdown`:
  - Used for markdown preview patterns in assistant/knowledge/document-like surfaces.

## Page Implementation Targets
- Kanban:
  - Drag-and-drop columns/cards, WIP limits, lane metrics, detail side panel.
- Gantt:
  - Timeline planning table with start/end windows, duration math, and dependency markers.
- Timeline:
  - Grouped chronological event feed with filters (source/severity/user), quick focus actions.
- Assistant:
  - Prompt input, answer cards, cited sources panel, structured result blocks.
- Chat:
  - Conversation view, model/runtime controls, context chips, metadata panel.
- Knowledge:
  - Search + facet filters + markdown preview.
- Documents:
  - File registry table, state badges, upload queue mock, pagination scaffold.
- Approvals:
  - Request queue, diff/reason panel, approve/reject flow with decision capture.
- Prompt Lab:
  - Prompt version list, editor panel, test-run simulator, publish/rollback actions.
- Agent Console:
  - Job queue, runtime stream log, budget/runtime KPI blocks, action controls.
- New Item:
  - Multi-section validated form with optimistic submit feedback and preview.

## Delivery Notes
- Maintain consistent token-driven styles and reusable UI primitives.
- Keep all templates seeded with mock data and isolated client-side state.
- Avoid dead-end UX by ensuring each page has at least one actionable workflow.
