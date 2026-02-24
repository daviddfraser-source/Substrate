# Start Here (Bootstrap)

Use this file to start a new Agentic IDE chat (e.g. VS Code + Antigravity, Cursor, Cline) quickly under this governance model.

## The Fast-Path (MCP Native)

If your agent supports MCP (Model Context Protocol), you do **not** need to manually run CLI commands to load context. The environment handles state injection natively. 

**Paste this prompt to begin a session:**

```text
Read AGENTS.md. We are using the Substrate MCP server. You already have ambient state for any active packets injected into your context. Use your `get_ready_packets` MCP tool to find work, `claim_packet` to claim it, and the `auto-done` skill to finalize it.
```

## The Fallback Path (CLI Only)

If you are using a legacy agent or terminal-only workflow without MCP support, follow this governed CLI bootstrap sequence:

1. **Bootstrap Context:**
   ```bash
   python3 substrate/.governance/wbs_cli.py briefing --format json
   ```
2. **Find Work:**
   ```bash
   python3 substrate/.governance/wbs_cli.py ready
   ```
3. **Claim & Contextualize:**
   ```bash
   python3 substrate/.governance/wbs_cli.py claim <PACKET_ID> codex
   python3 substrate/.governance/wbs_cli.py context <PACKET_ID> --format json --max-events 40 --max-notes-bytes 4000
   ```

## Fresh Clone Initialization

If this is a brand new repository clone, initialize the scaffold before starting work:

```bash
substrate/scripts/init-scaffold.sh substrate/templates/wbs-codex-minimal.json
```

Optional post-clone cleanup profile:

```bash
substrate/scripts/post-clone-cleanup.sh --profile codex-only --yes
```

## Break-Fix Quick Flow

When an unexpected break occurs (e.g. broken tests during execution) that requires governed scope:

```bash
python3 substrate/.governance/wbs_cli.py break-fix-open codex "Fix flaky suite" "Intermittent timeout" --severity high --packet <PACKET_ID>
python3 substrate/.governance/wbs_cli.py break-fix-start <BFIX_ID> codex
python3 substrate/.governance/wbs_cli.py break-fix-resolve <BFIX_ID> codex "Applied timeout + retry fix" --evidence substrate/tests/test_server_api.py
```

Operator guide: `substrate/docs/break-fix-workflow.md`
