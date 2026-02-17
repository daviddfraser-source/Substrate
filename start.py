#!/usr/bin/env python3
"""
WBS Orchestration Launcher
Cross-platform startup with delightful UX.
"""

import os
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

SCRIPT_DIR = Path(__file__).parent
CLI = SCRIPT_DIR / ".governance" / "wbs_cli.py"
SERVER = SCRIPT_DIR / ".governance" / "wbs_server.py"
STATE = SCRIPT_DIR / ".governance" / "wbs-state.json"
WBS_JSON = SCRIPT_DIR / ".governance" / "wbs.json"
SCAFFOLD_CONFIG = SCRIPT_DIR / "scaffold.config.json"

# Colors (respects NO_COLOR)
def c(code, text):
    if os.environ.get("NO_COLOR") or not sys.stdout.isatty():
        return text
    return f"\033[{code}m{text}\033[0m"

green = lambda t: c("32", t)
blue = lambda t: c("34", t)
bold = lambda t: c("1", t)
dim = lambda t: c("2", t)


def banner():
    print()
    print(bold("  +-------------------------------------------+"))
    print(bold("  |") + " WBS Orchestration for Agentic Delivery   " + bold("|"))
    print(bold("  +-------------------------------------------+"))
    print()


def run(cmd, capture=False):
    """Run a CLI command."""
    result = subprocess.run(
        [sys.executable, str(CLI)] + cmd,
        cwd=SCRIPT_DIR,
        capture_output=capture,
        text=True
    )
    return result


def load_scaffold_config():
    """Load scaffold config with sane defaults."""
    defaults = {
        "project_name": "Substrate Project",
        "default_agent": "substrate-lead",
        "dashboard_port": 8080,
        "wbs_template": "templates/wbs-codex-refactor.json",
        "wbs_file": ".governance/wbs.json",
        "enable_skills": [],
        "ci_profile": "full",
    }
    if not SCAFFOLD_CONFIG.exists():
        return defaults
    try:
        with open(SCAFFOLD_CONFIG) as f:
            data = json.load(f)
        defaults.update(data)
    except Exception:
        pass
    return defaults


def _validate_scaffold_data(config: Dict) -> List[str]:
    """Validate scaffold config values without external dependencies."""
    errors: List[str] = []

    required = {
        "project_name": str,
        "default_agent": str,
        "dashboard_port": int,
        "wbs_template": str,
        "wbs_file": str,
        "enable_skills": list,
        "ci_profile": str,
    }

    for key, expected_type in required.items():
        if key not in config:
            errors.append(f"missing required key: {key}")
            continue
        if not isinstance(config[key], expected_type):
            errors.append(f"invalid type for {key}: expected {expected_type.__name__}")

    if "dashboard_port" in config and isinstance(config["dashboard_port"], int):
        if not (1 <= config["dashboard_port"] <= 65535):
            errors.append("dashboard_port must be between 1 and 65535")

    if "ci_profile" in config and config.get("ci_profile") not in ("minimal", "full"):
        errors.append("ci_profile must be one of: minimal, full")

    if "enable_skills" in config and isinstance(config.get("enable_skills"), list):
        if not all(isinstance(item, str) and item.strip() for item in config["enable_skills"]):
            errors.append("enable_skills must contain non-empty strings")

    for key in ("project_name", "default_agent", "wbs_template", "wbs_file"):
        if key in config and isinstance(config[key], str) and not config[key].strip():
            errors.append(f"{key} must be a non-empty string")

    return errors


def validate_scaffold() -> Tuple[bool, List[str]]:
    """Validate scaffold config and WBS/schema contracts."""
    messages: List[str] = []
    ok = True

    config = load_scaffold_config()
    if SCAFFOLD_CONFIG.exists():
        try:
            with open(SCAFFOLD_CONFIG) as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            return False, [f"invalid JSON in scaffold config: {e}"]
        except OSError as e:
            return False, [f"unable to read scaffold config: {e}"]
    else:
        messages.append("scaffold config not found; validating with defaults")

    errors = _validate_scaffold_data(config)
    if errors:
        ok = False
        messages.extend(errors)

    template_path = SCRIPT_DIR / str(config.get("wbs_template", "")).strip()
    if not template_path.exists():
        ok = False
        messages.append(f"wbs_template not found: {template_path}")

    wbs_file = SCRIPT_DIR / str(config.get("wbs_file", "")).strip()
    if not wbs_file.exists():
        ok = False
        messages.append(f"wbs_file not found: {wbs_file}")

    for command, label in (
        (["validate"], "wbs validation"),
        (["validate-packet", str(template_path)], "template packet validation"),
    ):
        result = run(command, capture=True)
        if result.returncode != 0:
            ok = False
            detail = (result.stdout + result.stderr).strip()
            messages.append(f"{label} failed: {detail}")

    return ok, messages


def save_scaffold_config(config):
    with open(SCAFFOLD_CONFIG, "w") as f:
        json.dump(config, f, indent=2)
        f.write("\n")


def show_status_box():
    """Show a nice status summary."""
    result = run(["progress"], capture=True)
    lines = result.stdout.strip().split("\n")

    # Parse counts
    counts = {}
    for line in lines:
        if ":" in line and not line.startswith("-") and not line.startswith("="):
            parts = line.split(":")
            if len(parts) == 2:
                key = parts[0].strip().lower()
                val = parts[1].strip()
                if val.isdigit():
                    counts[key] = int(val)

    done = counts.get("done", 0)
    total = counts.get("total", 0)

    if total > 0:
        pct = int(100 * done / total)
        bar_width = 20
        filled = int(bar_width * done / total)
        bar = "#" * filled + "-" * (bar_width - filled)
        print(f"  Progress: [{green(bar)}] {pct}% ({done}/{total} packets)")
        print()


def get_next_action():
    """Get the recommended next action."""
    result = run(["next"], capture=True)
    return result.stdout.strip()


def interactive_menu():
    """Show interactive menu for first-time users."""
    print(dim("  What would you like to do?"))
    print()
    print(f"  {bold('1)')} Start working (show next action)")
    print(f"  {bold('2)')} See full status")
    print(f"  {bold('3)')} Open web dashboard")
    print(f"  {bold('4)')} Interactive setup wizard")
    print(f"  {bold('5)')} Scaffold onboarding wizard")
    print()

    try:
        choice = input(dim("  Enter choice [1]: ")).strip() or "1"
    except (KeyboardInterrupt, EOFError):
        print("\n")
        return

    print()

    if choice == "1":
        run(["next"])
    elif choice == "2":
        run(["status"])
    elif choice == "3":
        start_dashboard()
    elif choice == "4":
        run(["init", "--wizard"])
    elif choice == "5":
        scaffold_wizard()
    else:
        print(f"  Unknown choice: {choice}")


def start_dashboard(port="8080"):
    """Start the web dashboard."""
    if not STATE.exists():
        print("  Initializing database first...")
        run(["init", str(WBS_JSON)])

    print(f"  {green('*')} Dashboard: {bold(f'http://localhost:{port}')}")
    print(f"  {dim('Press Ctrl+C to stop')}")
    print()
    subprocess.run([sys.executable, str(SERVER), port])


def scaffold_wizard():
    """Scaffold-focused onboarding wizard."""
    cfg = load_scaffold_config()

    print(dim("  Substrate Onboarding Wizard"))
    print()

    name = input(dim(f"  Project name [{cfg['project_name']}]: ")).strip() or cfg["project_name"]

    print()
    print(dim("  WBS template profile:"))
    print("    1) minimal (fast bootstrap)")
    print("    2) full (comprehensive governance)")
    print("    3) refactor (legacy-compatible full)")
    template_choice = input(dim("  Choice [2]: ")).strip() or "2"
    template_map = {
        "1": "templates/wbs-codex-minimal.json",
        "2": "templates/wbs-codex-full.json",
        "3": "templates/wbs-codex-refactor.json",
    }
    template = template_map.get(template_choice, template_map["2"])

    port_raw = input(dim(f"  Dashboard port [{cfg['dashboard_port']}]: ")).strip() or str(cfg["dashboard_port"])
    if not port_raw.isdigit() or not (1 <= int(port_raw) <= 65535):
        print("  Invalid port, using 8080")
        port_raw = "8080"

    ci_profile = input(dim(f"  CI profile [full|minimal] [{cfg['ci_profile']}]: ")).strip().lower() or cfg["ci_profile"]
    if ci_profile not in ("full", "minimal"):
        ci_profile = "full"

    skill_profile = input(dim("  Skill profile [full|minimal] [full]: ")).strip().lower() or "full"
    if skill_profile == "minimal":
        skills = ["precommit-governance", "skill-authoring"]
    else:
        skills = [
            "agent-eval",
            "security-gates",
            "pr-review-automation",
            "precommit-governance",
            "ui-regression",
            "observability-baseline",
            "skill-authoring",
            "mcp-catalog-curation",
        ]

    cfg.update({
        "project_name": name,
        "dashboard_port": int(port_raw),
        "wbs_template": template,
        "ci_profile": ci_profile,
        "enable_skills": skills,
    })
    save_scaffold_config(cfg)

    print()
    print(f"  {green('*')} Saved scaffold config: {SCAFFOLD_CONFIG}")

    init_script = SCRIPT_DIR / "scripts" / "init-scaffold.sh"
    if init_script.exists():
        print(f"  {green('*')} Running scaffold init...")
        subprocess.run(["bash", str(init_script), template], cwd=SCRIPT_DIR, check=False)
    else:
        print("  init-scaffold script not found; run initialization manually.")


def parse_dashboard_port(args):
    """Parse and validate custom dashboard port from CLI args."""
    port = "8080"
    for i, arg in enumerate(args):
        if arg.startswith("--port="):
            port = arg.split("=", 1)[1]
            break
        if arg == "--port" and i + 1 < len(args):
            port = args[i + 1]
            break

    if not port.isdigit():
        print(f"Invalid port: {port}")
        print("Use an integer between 1 and 65535.")
        sys.exit(1)

    port_num = int(port)
    if port_num < 1 or port_num > 65535:
        print(f"Invalid port: {port}")
        print("Use an integer between 1 and 65535.")
        sys.exit(1)

    return str(port_num)


def main():
    os.chdir(SCRIPT_DIR)
    args = sys.argv[1:]

    # Direct flags (non-interactive)
    if "--wizard" in args:
        banner()
        run(["init", "--wizard"])
        print()
        run(["next"])
        return

    if "--wizard-scaffold" in args:
        banner()
        scaffold_wizard()
        return

    if "--dashboard" in args:
        port = parse_dashboard_port(args)
        banner()
        start_dashboard(port)
        return

    if "--status" in args:
        run(["progress"])
        return

    if "--validate" in args:
        valid, messages = validate_scaffold()
        if valid:
            print(green("Scaffold validation passed"))
            return
        print("Scaffold validation failed:")
        for message in messages:
            print(f"  - {message}")
        sys.exit(1)

    if "--help" in args or "-h" in args:
        print("Usage: python3 start.py [OPTIONS]")
        print()
        print("Options:")
        print("  (none)        Interactive menu")
        print("  --wizard      Guided project setup")
        print("  --wizard-scaffold  Guided scaffold onboarding setup")
        print("  --dashboard   Start web UI")
        print("  --port N      Custom dashboard port (use with --dashboard, default: 8080)")
        print("  --status      Quick progress summary")
        print("  --validate    Validate scaffold config and WBS/schema contracts")
        print()
        return

    # First run or interactive mode
    banner()

    if not STATE.exists():
        print(f"  {green('*')} First run — initializing project...")
        print()
        run(["init", str(WBS_JSON)])
        print()

    show_status_box()
    interactive_menu()


if __name__ == "__main__":
    main()
