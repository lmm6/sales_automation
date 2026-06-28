from langgraph.graph import StateGraph, END
from graph.state import SalesState
from graph.nodes import lead_master_node, proposal_crafter_node, joint_meeting_node
from graph.edges import should_continue, route_proposal, route_meeting

def build_sales_graph():
    workflow = StateGraph(SalesState)

    workflow.add_node("lead_master_node", lead_master_node)
    workflow.add_node("proposal_crafter_node", proposal_crafter_node)
    workflow.add_node("joint_meeting_node", joint_meeting_node)

    workflow.set_entry_point("lead_master_node")
    workflow.add_conditional_edges("lead_master_node", should_continue)
    workflow.add_conditional_edges("proposal_crafter_node", route_proposal)
    workflow.add_conditional_edges("joint_meeting_node", route_meeting)

    return workflow.compile()
