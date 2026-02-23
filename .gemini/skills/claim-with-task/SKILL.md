---
name: claim-with-task
description: Claim a governance packet and immediately synchronize its scope (required actions and validation checks) into your native conversational task.md checklist.
---

# Claim Packet & Sync Task

When you need to begin work on a new packet, use this skill to claim it and automatically set up your native VS Code UI `task.md` to reflect the strictly governed scope.

## 1. Claim the Packet
Use the `claim_packet` MCP tool to formally claim the packet in the governance state machine.
Example: `claim_packet(packet_id="VSX-16-3", agent="gemini")`

## 2. Retrieve the Packet Context
Use the `get_packet_context` MCP tool to fetch the full JSON definition of the packet you just claimed.
Example: `get_packet_context(packet_id="VSX-16-3")`

## 3. Extract Scope & Validation
Read the JSON response from step 2. Specifically look for:
- `required_actions` (or `scope` if no actions are listed item by item)
- `validation_checks`
- `exit_criteria`

## 4. Initialize `task.md`
Use the `write_to_file` tool to initialize (or overwrite if empty) your conversation's `task.md` with exactly the items from step 3. 

Format the file strictly as follows:

```markdown
# Task: [packet_id] — [title]

## Execution (Required Actions)
- [ ] Action 1
- [ ] Action 2

## Verification (Exit Criteria)
- [ ] Validation check 1
- [ ] Validation check 2
```

## 5. Proceed with Execution
Call the `task_boundary` tool to visibly enter the execution phase in the VS Code UI. Set the `TaskName` to the packet title and begin executing the checklist.
