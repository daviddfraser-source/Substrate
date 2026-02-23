---
name: ralph-wiggum
description: Pre-action self-check at governance state boundaries (claim and done). Run this before claiming a packet or marking one done. Surfaces hidden assumptions and gaps in evidence before they are committed to the audit trail.
---

# Ralph Wiggum Self-Check

Use this skill at two moments only:
- **Before `claim`** — to surface scope assumptions
- **Before `done`** — to verify evidence quality

---

## Pre-Claim Checklist

Work through these before running `claim <PACKET_ID> gemini`:

1. **What packet am I claiming?**
   - Read the full `required_actions` list — not just the packet title or scope summary.

2. **What am I assuming that isn't written there?**
   - State your assumptions explicitly, even if they seem obvious.
   - Example: *"I am assuming the new file goes in substrate/docs/ — that is not stated."*

3. **Is there any ambiguity I should resolve before proceeding?**
   - If yes: stop, ask the user, get clarification before claiming.
   - If no: state that explicitly before proceeding.

4. **Which files will I touch?**
   - List expected files/directories.
   - Confirm each is within the packet's defined scope.

**Decision gate:** If you have unanswered ambiguities → ask the user. If all clear → claim and proceed.

---

## Pre-Done Checklist

Work through these before running `done <PACKET_ID> gemini "evidence" --risk none`:

1. **What file(s) did I change or create?**
   - Name every file. Include relative paths from the repo root.

2. **What validation did I run?**
   - Name the exact command(s) and their outcomes.
   - Example: `make hygiene` → exit 0; `Select-String` found 4 expected headings.

3. **Does my evidence string capture all of the above?**
   - Read it back. If a reviewer could not tell what changed, where it is, and how it was validated → rewrite before marking done.

**Decision gate:** Evidence string complete → mark done. Evidence string incomplete → fix it first.

---

## Example Application

### Pre-Claim (good)

> *"I am claiming RW-15-3. required_actions says create `.gemini/skills/ralph-wiggum/SKILL.md`
> with YAML frontmatter and two checklists. I am assuming the file goes in the same skills
> directory as other Gemini skills — confirmed by checking `.gemini/skills/`. No ambiguity.
> Proceeding."*

### Pre-Done (good)

> *"Created `.gemini/skills/ralph-wiggum/SKILL.md` (68 lines). Validated: YAML frontmatter
> parses, both checklists present, non-goals section included. Evidence string names the file,
> line count, and validation method — ready to mark done."*

### Pre-Done (bad — do not do this)

> *"Done. Added the skill."*  ← Rejected by constitution.md Article III §1.

---

## Non-Goals

- This is **not** a general step-by-step narration of every action.
- It applies **only** at the two `claim` and `done` governance boundaries.
- For complex packets needing architectural decisions: use full plan-mode, not just this checklist.
