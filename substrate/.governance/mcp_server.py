import os
import sys
import subprocess
import json
from mcp.server.fastmcp import FastMCP

# Ensure commands run from the repo root
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(os.path.join(REPO_ROOT, "substrate", ".governance"))
import update_ambient_state
mcp = FastMCP("Substrate Governance")

# Ensure commands run from the repo root
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CLI_PATH = os.path.join("substrate", ".governance", "wbs_cli.py")

def run_wbs_cli(*args):
    """Helper to run the wbs_cli.py subprocess and capture output."""
    cmd = ["python", CLI_PATH] + list(args)
    try:
        result = subprocess.run(
            cmd,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Command failed with exit code {e.returncode}.\nOutput:\n{e.stdout}\nErrors:\n{e.stderr}"

@mcp.tool()
def get_ready_packets() -> str:
    """Get a list of all packets that are unblocked and ready to be claimed."""
    return run_wbs_cli("ready")

@mcp.tool()
def get_status() -> str:
    """Get the full status of all WBS areas and packets in the project."""
    return run_wbs_cli("status")

@mcp.tool()
def get_packet_context(packet_id: str) -> str:
    """
    Get the rigorous context bundle for a specific packet, including its scope,
    history, and references.
    """
    return run_wbs_cli("context", packet_id, "--format", "json")

@mcp.tool()
def claim_packet(packet_id: str, agent: str) -> str:
    """
    Claim a packet for execution. You MUST claim a packet before working on it.
    Example: claim_packet("VSX-16-1", "gemini")
    """
    result = run_wbs_cli("claim", packet_id, agent)
    update_ambient_state.update_ambient_state(agent)
    return result

@mcp.tool()
def mark_packet_done(packet_id: str, agent: str, evidence_notes: str, risk_declared: str = "none") -> str:
    """
    Mark a claimed, in-progress packet as DONE.
    You MUST provide an exhaustive evidence_notes string detailing what changed, where,
    and how it was validated.
    risk_declared should be 'none' unless you have specifically filed a residual risk.
    """
    result = run_wbs_cli("done", packet_id, agent, evidence_notes, "--risk", risk_declared)
    update_ambient_state.update_ambient_state(agent)
    return result

@mcp.tool()
def log_activity(limit: int = 15) -> str:
    """Get the most recent activity log entries for the project."""
    return run_wbs_cli("log", str(limit))

if __name__ == "__main__":
    # Allow running directly for debugging
    mcp.run(transport="stdio")
