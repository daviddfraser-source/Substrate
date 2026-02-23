#!/usr/bin/env python3
"""
sandbox.py — Governance sandbox lifecycle manager.

Creates, inspects, resets, and tears down an isolated sandbox project
using the existing multi-project governance infrastructure.

Usage:
    python substrate/scripts/sandbox.py create [--seed <wbs-json>]
    python substrate/scripts/sandbox.py reset  [--seed <wbs-json>]
    python substrate/scripts/sandbox.py status
    python substrate/scripts/sandbox.py destroy
    python substrate/scripts/sandbox.py shell-env

The sandbox project is named 'sandbox' and lives at:
    substrate/projects/sandbox/

All governance rules apply identically inside the sandbox — it is NOT
a no-op mode. It is a separate, disposable project namespace.

Environment variable set when using 'shell-env':
    WBS_PROJECT=sandbox

Exit codes:
    0  success
    1  error
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Resolve repo root relative to this script's location
SCRIPT_DIR = Path(__file__).resolve().parent
SUBSTRATE_ROOT = SCRIPT_DIR.parent
REPO_ROOT = SUBSTRATE_ROOT.parent
GOV_DIR = SUBSTRATE_ROOT / ".governance"
CLI = [sys.executable, str(GOV_DIR / "wbs_cli.py")]

SANDBOX_PROJECT_ID = "sandbox"
SANDBOX_DIR = SUBSTRATE_ROOT / "projects" / SANDBOX_PROJECT_ID
SANDBOX_APPROVAL = "WBS-APPROVED:SANDBOX-LIFECYCLE"

# Default seed: use the governance wbs.json as the sandbox WBS definition
DEFAULT_SEED = GOV_DIR / "wbs.json"


def run(*args, check=True, capture=False, **kwargs):
    """Run a subprocess and return the result."""
    cmd = list(args)
    result = subprocess.run(cmd, capture_output=capture, text=True, **kwargs)
    if check and result.returncode != 0:
        if capture:
            print(result.stdout, end="")
            print(result.stderr, end="", file=sys.stderr)
        sys.exit(result.returncode)
    return result


def cli(*args, **kwargs):
    """Run the governance CLI with the given arguments."""
    return run(*CLI, *args, **kwargs)


def cmd_create(seed: str = ""):
    """Create the sandbox project."""
    if SANDBOX_DIR.exists():
        print(f"[sandbox] Already exists at {SANDBOX_DIR}")
        print("[sandbox] Use 'reset' to wipe and recreate, or 'status' to inspect.")
        sys.exit(1)

    seed_path = Path(seed) if seed else DEFAULT_SEED
    if not seed_path.exists():
        print(f"[sandbox] Seed file not found: {seed_path}")
        sys.exit(1)

    # Create project directory and copy WBS definition into it
    print(f"[sandbox] Creating sandbox project from: {seed_path}")
    SANDBOX_DIR.mkdir(parents=True, exist_ok=True)
    sandbox_wbs = SANDBOX_DIR / "wbs.json"
    sandbox_state = SANDBOX_DIR / "wbs-state.json"
    import shutil as _shutil
    _shutil.copy2(seed_path, sandbox_wbs)

    # Use env vars to point the CLI at sandbox-specific files.
    # WBS_STATE_PATH works with the legacy CLI; WBS_PROJECT works with multi-project CLI.
    env = {
        **os.environ,
        "WBS_PROJECT": SANDBOX_PROJECT_ID,
        "WBS_STATE_PATH": str(sandbox_state),
        "WBS_DEF_PATH": str(sandbox_wbs),
    }
    result = subprocess.run(
        CLI + ["init", str(sandbox_wbs)],
        env=env, text=True, capture_output=True
    )
    print(result.stdout, end="")

    # The CLI may write state to the default path — move it if needed
    gov_state = GOV_DIR / "wbs-state.json"
    if not sandbox_state.exists() and gov_state.exists():
        # State was written to default location; we don't move it (that's the real state)
        # Instead, initialize state manually
        import json as _json
        wbs = _json.loads(sandbox_wbs.read_text())
        state = {
            "version": "1.0",
            "created_at": __import__("datetime").datetime.now().isoformat(),
            "updated_at": __import__("datetime").datetime.now().isoformat(),
            "packets": {
                p["id"]: {"status": "pending", "assigned_to": None,
                           "started_at": None, "completed_at": None, "notes": None}
                for p in wbs.get("packets", [])
            },
            "log": [],
            "area_closeouts": {},
            "log_integrity_mode": "plain",
            "operator_mode": "balanced",
            "mode_overrides": {}
        }
        sandbox_state.write_text(_json.dumps(state, indent=2) + "\n")
        print(f"[sandbox] Initialized state with {len(state['packets'])} packets")

    if result.returncode != 0 and not sandbox_state.exists():
        print(result.stderr, end="", file=sys.stderr)
        sys.exit(result.returncode)

    print(f"[sandbox] ✓ Sandbox ready at: {SANDBOX_DIR}")
    print()
    print("[sandbox] To work in sandbox scope, set the CLI path overrides:")
    print(f"    $env:WBS_STATE_PATH = '{sandbox_state}'  # PowerShell")
    print(f"    $env:WBS_DEF_PATH   = '{sandbox_wbs}'")
    print()
    print(f"    export WBS_STATE_PATH='{sandbox_state}'  # bash")
    print(f"    export WBS_DEF_PATH='{sandbox_wbs}'")
    print()
    print("[sandbox] When done, tear it down:")
    print("    python substrate/scripts/sandbox.py destroy")


def cmd_reset(seed: str = ""):
    """Wipe and recreate the sandbox project."""
    if SANDBOX_DIR.exists():
        print(f"[sandbox] Destroying existing sandbox at {SANDBOX_DIR}")
        shutil.rmtree(SANDBOX_DIR)
    cmd_create(seed)


def cmd_status():
    """Show the current sandbox project status."""
    if not SANDBOX_DIR.exists():
        print("[sandbox] No sandbox project found.")
        print("[sandbox] Create one with: python substrate/scripts/sandbox.py create")
        sys.exit(0)

    state_path = SANDBOX_DIR / "wbs-state.json"
    wbs_path = SANDBOX_DIR / "wbs.json"

    print(f"[sandbox] Project directory : {SANDBOX_DIR}")
    print(f"[sandbox] WBS definition    : {wbs_path} ({'exists' if wbs_path.exists() else 'MISSING'})")
    print(f"[sandbox] State file        : {state_path} ({'exists' if state_path.exists() else 'MISSING'})")

    if state_path.exists():
        import json as _json
        state = _json.loads(state_path.read_text())
        packets = state.get("packets", {})
        by_status: dict = {}
        for p, s in packets.items():
            st = s.get("status", "unknown")
            by_status.setdefault(st, []).append(p)
        print(f"\n[sandbox] Packets: {len(packets)}")
        for st, ids in sorted(by_status.items()):
            print(f"  {st:12s}: {len(ids)}")
        in_progress = by_status.get("in_progress", [])
        if in_progress:
            print(f"\n[sandbox] In-progress: {', '.join(in_progress)}")
    else:
        print("[sandbox] No state file — sandbox was not fully initialized.")


def cmd_destroy():
    """Destroy the sandbox project entirely."""
    if not SANDBOX_DIR.exists():
        print("[sandbox] No sandbox project found — nothing to destroy.")
        sys.exit(0)

    print(f"[sandbox] Destroying: {SANDBOX_DIR}")
    import stat

    def _remove_readonly(func, path, _exc):
        """Clear read-only bit and retry — required on Windows."""
        os.chmod(path, stat.S_IWRITE)
        func(path)

    shutil.rmtree(SANDBOX_DIR, onerror=_remove_readonly)
    print("[sandbox] ✓ Sandbox destroyed.")


def cmd_shell_env():
    """Print shell commands to set the sandbox environment."""
    print(f"# Run one of these to enter sandbox scope:")
    print(f"$env:WBS_PROJECT = '{SANDBOX_PROJECT_ID}'  # PowerShell")
    print(f"export WBS_PROJECT={SANDBOX_PROJECT_ID}    # bash/zsh")
    print()
    print(f"# To exit sandbox scope:")
    print(f"Remove-Item Env:\\WBS_PROJECT   # PowerShell")
    print(f"unset WBS_PROJECT              # bash/zsh")


COMMANDS = {
    "create": cmd_create,
    "reset": cmd_reset,
    "status": cmd_status,
    "destroy": cmd_destroy,
    "shell-env": cmd_shell_env,
}


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    cmd = args[0]
    if cmd not in COMMANDS:
        print(f"[sandbox] Unknown command: {cmd}")
        print(f"[sandbox] Available: {', '.join(COMMANDS)}")
        sys.exit(1)

    fn = COMMANDS[cmd]
    # Pass --seed if given
    seed = ""
    for i, a in enumerate(args[1:], 1):
        if a == "--seed" and i + 1 < len(args):
            seed = args[i + 1]
            break

    if cmd in ("create", "reset"):
        fn(seed)
    else:
        fn()


if __name__ == "__main__":
    main()
