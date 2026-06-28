from langgraph.graph import StateGraph, END
from graph.state import SalesState
from graph.nodes import lead_master_node, proposal_crafter_node
from graph.edges import should_continue

def build_sales_graph():
    workflow = StateGraph(SalesState)

    # 节点
    workflow.add_node("lead_master_node", lead_master_node)
    workflow.add_node("proposal_crafter_node", proposal_crafter_node)

    # 边
    workflow.set_entry_point("lead_master_node")
    workflow.add_conditional_edges("lead_master_node", should_continue)
    workflow.add_edge("proposal_crafter_node", END)

    return workflow.compile()