---
name: auto-done
description: Automated pre-flight check and programmatic evidence generator. Runs git diffs and synthesizes terminal outputs to construct a complete evidence string, then marks the active packet done via MCP.
---

# Auto-Done Verification & Execution

Use this skill when you have completed all strictly required actions for the active governance packet and are ready to mark it `DONE`. 

This replaces the manual "Ralph Wiggum" self-check by instructing you to algorithmically gather the evidence yourself before submitting the MCP tool call.

## 1. Gather Code Evidence
Use your `run_command` tool to execute:
`git diff --name-status` (or `git status -s`)

This identifies exactly which files you have added, deleted, or modified.

## 2. Gather Validation Evidence
Recall the tests, lints, or scripts you ran during your execution phase. 
Identify the final exit status (e.g., exit code 0) or the exact output snippet that proves the validation succeeded.

## 3. Synthesize the Evidence String
Construct a dense, exhaustive string summarizing steps 1 and 2. 
**Format:** "Modified [file_a, file_b]. Created [file_c]. Validated via [command run] (result: [exit code/output snippet])."

## 4. Execute the Closeout
Finally, call the `mark_packet_done` MCP tool. 
- `packet_id`: The ID of the packet you just finished.
- `agent`: "gemini"
- `evidence_notes`: The exact string synthesized in Step 3.
- `risk_declared`: "none" (unless you have explicitly opened a residual risk via the CLI).

## 5. Clean up Task UI
If you have a `task.md` open for this packet, mark all Execution and Verification steps as complete `[x]`, and then update your `task_boundary` mode to `VERIFICATION` or back to `PLANNING` for your next packet.
