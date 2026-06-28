def should_continue(state: dict):
    if state["lead_score"] >= 70:
        return "proposal_crafter_node"
    return "end"