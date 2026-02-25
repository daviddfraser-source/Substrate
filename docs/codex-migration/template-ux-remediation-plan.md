# Template UX Remediation Plan

## 1. Context and Objective
This document outlines the plan to migrate 11 template pages in `templates/ai-substrate/app` away from the Ant Design (`antd`) dependency, replacing them with a custom lightweight component library. This ensures consistent styling based on our design system and drastically reduces our bundle footprint.

## 2. Ant Design Component Audit
Based on mapping the files in `templates/ai-substrate/app/**/*.tsx`, the following antd components are currently in use across the templates:

| Antd Component | Pages Used In |
| --- | --- |
| `Alert` | assistant, gantt, kanban |
| `Avatar` | chat |
| `Button` | agent-console, approvals, assistant, chat, documents, new, prompt-lab |
| `Card` | agent-console, approvals, assistant, chat, documents, gantt, kanban, knowledge, new, prompt-lab, timeline |
| `Col` | agent-console, assistant |
| `Descriptions` | approvals |
| `Drawer` | approvals |
| `Form` | approvals, assistant, new |
| `Input` | approvals, assistant, chat, documents, knowledge, new, prompt-lab, timeline |
| `Progress` | agent-console, chat |
| `Row` | agent-console, assistant |
| `Segmented` | chat, gantt, prompt-lab |
| `Select` | documents, knowledge, new, timeline |
| `Space` | agent-console, approvals, assistant, chat, documents, gantt, kanban, knowledge, new, prompt-lab, timeline |
| `Statistic` | agent-console, kanban |
| `Table` | agent-console, approvals, documents |
| `Tag` | agent-console, approvals, assistant, chat, documents, knowledge, new, prompt-lab, timeline |
| `Timeline` | timeline |
| `Tree` | knowledge |
| `Typography` | agent-console, approvals, assistant, chat, documents, gantt, kanban, knowledge, new, prompt-lab, timeline |
| `Upload` | documents |
| `message` | approvals, documents |

## 3. Component Mapping Matrix (antd → custom)

| Antd Component | Target Custom Component / Approach |
| --- | --- |
| `Button` | `ui/button.tsx` |
| `Card` | `ui/card.tsx` |
| `Input` | `ui/input.tsx` |
| `Tag` | `ui/badge.tsx` (for generic tags) or `governance/StatusBadge.tsx` (for statuses) |
| `Statistic` | `governance/KpiCard.tsx` |
| `Tree` | `governance/TreeView.tsx` |
| `Space`, `Row`, `Col` | Replace with standard CSS flex/grid container wrappers (`<div className="flex gap-4...">`) |
| `Typography` | Replace with semantic HTML (`<h1>`, `<p>`, `<span>`) and CSS utility classes |
| `Form`, `Descriptions` | Replace with semantic HTML (`<form>`, `<dl>`) natively |
| `Progress` | Use `governance/ProgressRing.tsx` when circular, or build a new simple linear `ui/progress.tsx` if a bar is needed. |

### Missing Custom Components to Create

The following components do not currently have a custom equivalent and must be created in `components/ui` as part of their respective page migrations:

- **`Table`**: Generic data presentation table (`ui/table.tsx`).
- **`Select`**: Custom dropdown (`ui/select.tsx`).
- **`Alert`**: Information callout banners (`ui/alert.tsx`).
- **`Toast` / `message`**: Lightweight notification system (`ui/toast.tsx` or similar).
- **`Segmented`**: Button group / tab switcher (`ui/tabs.tsx` or `ui/segmented.tsx`).
- **`Timeline`**: Vertical chronological list (`ui/timeline.tsx`).
- **`Drawer`**: Right-side sliding panel (`ui/drawer.tsx`).
- **`Upload`**: File drag-and-drop zone (`ui/upload.tsx`).
- **`Avatar`**: Simple user icon container (`ui/avatar.tsx`).

## 4. Migration Plan

The migration will follow a page-by-page packet execution order, defined in `wbs-template-ux-fix-proposal.json`.

**Per-Page Migration Checklist:**
1. Create or ensure availability of required custom `ui/*` components.
2. Remove all `antd` imports from the page file.
3. Import replacement components from `components/ui` or `components/governance`.
4. Refactor layout helpers (`Space`, `Row`, `Col`, `Typography`) into native HTML/CSS implementations utilizing our design variables.
5. Visually test the component mapping (e.g., verifying `StatusBadge` takes appropriate states).
6. Validate that `npm run dev` builds successfully and page loads HTTP 200.

**Final Cleanup:**
- Remove `antd` from `package.json` dependencies.
- Verify global bundle size improvements and remove `import "antd/dist/reset.css"` from `layout.tsx`.
