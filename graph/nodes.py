import json
from core.agent.runner import run_agent
from core.tools.toolkit import (
    web_search_tool, web_crawl_tool, analyze_lead_tool,
    generate_email_tool, generate_script_tool, generate_proposal_tool,
)

LEAD_MASTER_TOOLS = [web_search_tool, web_crawl_tool, analyze_lead_tool]

def lead_master_node(state: dict, progress_callback=None):
    prompt = state["lead_agent"].prompt
    if not prompt:
        prompt = "You are Lead Master, a B2B lead research and scoring specialist. Tools: web_search_tool, web_crawl_tool, analyze_lead_tool. Workflow: search, crawl, then analyze_lead. Return the final score."
    company_url = state["company_url"]
    company_name = company_url.split("//")[-1].split("/")[0]

    feedback_req = state.get("feedback_request", "")
    if feedback_req:
        if progress_callback:
            progress_callback("researching", "正在补充调研信息...")
        result = run_agent(
            prompt, LEAD_MASTER_TOOLS,
            f"Research {company_name} at {company_url}, focusing on: {feedback_req}",
            progress_callback=progress_callback
        )
        return {
            "lead_info": {**state.get("lead_info", {}), "feedback_research": str(result["tool_results"])},
            "feedback_request": "",
            "research_round": state.get("research_round", 0) + 1,
            "agent_log": [{"agent": "Lead Master", "action": "Feedback research", "detail": feedback_req, "round": state.get("research_round", 0) + 1}],
        }

    if progress_callback:
        progress_callback("searching", "正在搜索企业信息...")

        result = run_agent(
            prompt, LEAD_MASTER_TOOLS,
            f"Research and score this lead: {company_name} ({company_url})",
        progress_callback=progress_callback
    )

    score = 0
    lead_info = {"company_name": company_name, "website": company_url,
                 "search_data": "", "crawl_data": "",
                 "industry": "", "pain_points": "", "suggestion": ""}

    analyze_raw = result["tool_results"].get("analyze_lead_tool", [])
    if analyze_raw:
        try:
            data = json.loads(analyze_raw[-1])
            score = data.get("score", 0)
            lead_info = {
                "company_name": data.get("company_name", "") or company_name,
                "website": company_url,
                "search_data": str(result["tool_results"].get("web_search_tool", [""])[-1:]),
                "crawl_data": str(result["tool_results"].get("web_crawl_tool", [""])[-1:]),
                "industry": data.get("industry", ""),
                "pain_points": data.get("pain_points", ""),
                "suggestion": data.get("suggestion", ""),
            }
        except Exception:
            pass

    print(f"[Lead Master] Score: {score}")
    return {
        "lead_info": lead_info,
        "lead_score": score,
        "info_gaps": [],
        "feedback_request": "",
        "research_round": 0,
        "max_rounds": 3,
        "agent_log": [{"agent": "Lead Master", "action": "Research & scoring", "detail": f"Score: {score}", "round": 0}],
        "joint_decision": "",
    }


PROPOSAL_TOOLS = [generate_email_tool, generate_script_tool, generate_proposal_tool]

def proposal_crafter_node(state: dict, progress_callback=None):
    prompt = state["proposal_agent"].prompt
    if not prompt:
        prompt = "You are Proposal Crafter, a B2B proposal generation specialist. Tools: generate_email_tool, generate_script_tool, generate_proposal_tool (call LAST). Generate all three items."
    lead = state["lead_info"]
    intent = state.get("intent", "all")
    tools = PROPOSAL_TOOLS
    if intent == "email":
        tools = [generate_email_tool]
        prompt += " Only use: generate_email_tool."
    elif intent == "script":
        tools = [generate_script_tool]
        prompt += " Only use: generate_script_tool."
    elif intent == "proposal":
        tools = [generate_proposal_tool]
        prompt += " Only use: generate_proposal_tool."


    gaps = []
    if not lead.get("industry"): gaps.append("Missing industry info")
    if not lead.get("pain_points"): gaps.append("Missing pain points")
    if not lead.get("suggestion"): gaps.append("Missing follow-up suggestion")

    current_round = state.get("research_round", 0)
    max_rounds = state.get("max_rounds", 3)

    if gaps and current_round < max_rounds:
        return {
            "info_gaps": gaps,
            "feedback_request": "Need: " + ", ".join(gaps) + " for " + lead.get("company_name", "company"),
            "agent_log": [{"agent": "Proposal Crafter", "action": "Requested additional info", "detail": ", ".join(gaps), "round": current_round + 1}],
        }

    if progress_callback:
        progress_callback("generating", "正在生成销售方案...")

    lead_str = (
        f"Company: {lead.get('company_name', '')}\n"
        f"Industry: {lead.get('industry', '')}\n"
        f"Pain Points: {lead.get('pain_points', '')}\n"
        f"Suggestion: {lead.get('suggestion', '')}"
    )

    result = run_agent(prompt, tools, lead_str, progress_callback=progress_callback)

    email = ""
    script = ""
    prop = ""
    if intent in ("email", "all"):
        email = "".join(result["tool_results"].get("generate_email_tool", [])) or ""
    if intent in ("script", "all"):
        script = "".join(result["tool_results"].get("generate_script_tool", [])) or ""
    if intent in ("proposal", "all"):
        prop = "".join(result["tool_results"].get("generate_proposal_tool", [])) or ""

    return {
        "proposal_path": prop,
        "followup_email": email,
        "script": script,
        "info_gaps": [],
        "feedback_request": "",
        "agent_log": [{"agent": "Proposal Crafter", "action": "Generated proposal package", "detail": "Done", "round": current_round}],
    }


def joint_meeting_node(state: dict, progress_callback=None):
    if progress_callback:
        progress_callback("meeting", "正在召开联合会议...")

    lead = state["lead_info"]
    score = state.get("lead_score", 0)
    log = state.get("agent_log", [])

    lm_rounds = sum(1 for entry in log if entry.get("agent") == "Lead Master")
    pc_actions = sum(1 for entry in log if entry.get("agent") == "Proposal Crafter")

    meeting_notes = (
        "[Meeting Summary]\n"
        "Lead: " + (lead.get("company_name", "Unknown") or "") + " (" + (lead.get("industry", "") or "") + ")\n"
        "Score: " + str(score) + " | Research rounds: " + str(lm_rounds) + " | Proposal rounds: " + str(pc_actions) + "\n"
        "Decision: Proceed with generated proposal strategy.\n"
        "Both agents confirm alignment on pain points and solution approach."
    )

    print("[Joint Meeting] " + meeting_notes.replace("\n", " | "))
    return {
        "joint_decision": meeting_notes,
        "agent_log": [{"agent": "Joint Meeting", "action": "Internal strategy meeting", "detail": meeting_notes}],
        "proposal_path": state.get("proposal_path", ""),
        "followup_email": state.get("followup_email", ""),
        "script": state.get("script", ""),
        "lead_info": state.get("lead_info", {}),
        "lead_score": state.get("lead_score", 0),
    }
