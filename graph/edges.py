def should_continue(state: dict):
    if state["lead_score"] >= 80:
        return "proposal_crafter_node"
    return "end"

def route_proposal(state: dict):
    if state.get("feedback_request") and state.get("research_round", 0) < state.get("max_rounds", 3):
        return "lead_master_node"
    return "joint_meeting_node"

def route_meeting(state: dict):
    return "end"
