import os
import json

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
WBS_STATE_PATH = os.path.join(REPO_ROOT, "substrate", ".governance", "wbs-state.json")
WBS_DEF_PATH = os.path.join(REPO_ROOT, "substrate", ".governance", "wbs.json")
def get_agent_inject_path(agent):
    if agent == "gemini":
        dir_name = ".gemini"
    elif agent == "claude":
        dir_name = ".claude"
    elif agent == "codex":
        dir_name = ".codex"
    else:
        dir_name = f".{agent}"
    
    agent_dir = os.path.join(REPO_ROOT, dir_name)
    os.makedirs(agent_dir, exist_ok=True)
    return os.path.join(agent_dir, "system_prompt_addition.md")

def get_active_packet(agent="gemini"):
    """Finds the first IN_PROGRESS packet owned by the specified agent."""
    if not os.path.exists(WBS_STATE_PATH):
        return None
    try:
        with open(WBS_STATE_PATH, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        for packet_id, data in state.get("packets", {}).items():
            if data.get("status") == "in_progress" and data.get("assigned_to") == agent:
                return packet_id
    except Exception:
        pass
    return None

def get_packet_details(packet_id):
    """Retrieves packet definition from wbs.json."""
    if not os.path.exists(WBS_DEF_PATH):
        return None
    try:
        with open(WBS_DEF_PATH, 'r', encoding='utf-8') as f:
            wbs = json.load(f)
            
        for packet in wbs.get("packets", []):
            if packet.get("id") == packet_id:
                return packet
    except Exception:
        pass
    return None

def update_ambient_state(agent="gemini"):
    """Reads current state and updates the system prompt addition."""
    active_packet_id = get_active_packet(agent)
    
    inject_path = get_agent_inject_path(agent)
    
    if not active_packet_id:
        # Clear out the ambient state if no packet is active
        with open(inject_path, 'w', encoding='utf-8') as f:
            f.write("No active governance packet is currently claimed.\n")
        return

    packet_def = get_packet_details(active_packet_id)
    if not packet_def:
        return

    # Construct the ambient state string
    content = [
        f"You are currently executing governance packet: **{active_packet_id}** ({packet_def.get('title')})",
        "",
        "### Required Actions / Scope",
    ]
    
    if "scope" in packet_def and isinstance(packet_def["scope"], str):
        content.append(packet_def["scope"])
    
    for action in packet_def.get("required_actions", []):
        content.append(f"- {action}")
        
    content.append("")
    content.append("### Exit Criteria (Validation)")
    for check in packet_def.get("validation_checks", []) + packet_def.get("exit_criteria", []):
        content.append(f"- {check}")
        
    content.append("")
    content.append(f"*Note: You must use the `wbs_cli.py done` tool (or MCP tool) with exhaustive evidence to advance this state once complete.*")

    with open(inject_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(content))

if __name__ == "__main__":
    import sys
    agent = sys.argv[1] if len(sys.argv) > 1 else "gemini"
    update_ambient_state(agent)
