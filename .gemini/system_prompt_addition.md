You are currently executing governance packet: **VSX-16-2** (Ephemeral Context & Ambient State Injection)

### Required Actions / Scope
Develop a mechanism (e.g., a .gemini/system_prompt_addition.md scraper or workspace setting) that automatically injects the current active packet's scope (required_actions and exit_criteria) into the agent's context window. Implement a background watcher that updates this context whenever wbs-state.json changes.

### Exit Criteria (Validation)

*Note: You must use the `wbs_cli.py done` tool (or MCP tool) with exhaustive evidence to advance this state once complete.*