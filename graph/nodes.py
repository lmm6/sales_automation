import time
import random
from core.tools.toolkit import *

def lead_master_node(state: dict):
    company_url = state["company_url"]
    company_name = company_url.split("//")[-1].split("/")[0]

    feedback_req = state.get("feedback_request", "")
    if feedback_req:
        print(f"\n[Lead Master] Feedback research: {feedback_req}")
        search_result = web_search(f"{company_name} {feedback_req}")
        crawl_result = web_crawl(company_url)
        new_info = {
            "search_data": search_result,
            "crawl_data": str(crawl_result)[:1000],
            "feedback_research": str(search_result)[:1000],
        }
        log_entry = {
            "agent": "Lead Master",
            "action": "Feedback research",
            "detail": feedback_req,
            "round": state.get("research_round", 0) + 1,
        }
        return {
            "lead_info": {**state.get("lead_info", {}), **new_info},
            "feedback_request": "",
            "research_round": state.get("research_round", 0) + 1,
            "agent_log": [log_entry],
        }

    # Initial research
    print("\n[Lead Master] Mining lead...")
    search_result = web_search(f"{company_name} company intro business scale industry")
    crawl_result = web_crawl(company_url)
    result = analysis(company_name, search_result, crawl_result)

    lead_info = {
        "company_name": company_name,
        "website": state["company_url"],
        "search_data": search_result,
        "crawl_data": str(crawl_result)[:1000],
        "industry": result.get("industry", ""),
        "pain_points": result.get("pain_points", ""),
        "suggestion": result.get("suggestion", ""),
    }
    score = result.get("score", 0)

    print(f"[Lead Master] Score: {score}")

    log_entry = {
        "agent": "Lead Master",
        "action": "Initial research & scoring",
        "detail": f"Score: {score}, Industry: {lead_info.get('industry', '')}",
        "round": 0,
    }

    return {
        "lead_info": lead_info,
        "lead_score": score,
        "info_gaps": [],
        "feedback_request": "",
        "research_round": 0,
        "max_rounds": 3,
        "agent_log": [log_entry],
        "joint_decision": "",
    }


def proposal_crafter_node(state: dict):
    print("\n[Proposal Crafter] Analyzing lead...")
    lead = state["lead_info"]

    think_time = random.uniform(0.5, 2.0)
    print(f"[Proposal Crafter] Thinking ({think_time:.1f}s)...")
    time.sleep(think_time)

    gaps = []
    if not lead.get("industry"):
        gaps.append("Missing industry info")
    if not lead.get("pain_points"):
        gaps.append("Missing pain points")
    if not lead.get("suggestion"):
        gaps.append("Missing follow-up suggestion")

    current_round = state.get("research_round", 0)
    max_rounds = state.get("max_rounds", 3)

    if gaps and current_round < max_rounds:
        feedback_q = "Need more details: " + ", ".join(gaps) + " for " + lead.get("company_name", "this company")
        log_entry = {
            "agent": "Proposal Crafter",
            "action": "Requested additional info",
            "detail": feedback_q,
            "round": current_round + 1,
        }
        return {
            "info_gaps": gaps,
            "feedback_request": feedback_q,
            "agent_log": [log_entry],
        }

    print("[Proposal Crafter] Generating proposal, email, script...")
    prop = generate_proposal(lead)
    email = generate_email(lead)
    script = generate_script(lead)

    log_entry = {
        "agent": "Proposal Crafter",
        "action": "Generated proposal package",
        "detail": "Proposal: " + (prop or "N/A"),
        "round": current_round,
    }

    return {
        "proposal_path": prop,
        "followup_email": email,
        "script": script,
        "info_gaps": [],
        "feedback_request": "",
        "agent_log": [log_entry],
    }


def joint_meeting_node(state: dict):
    print("\n[Joint Meeting] Lead Master + Proposal Crafter meeting...")
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

    log_entry = {
        "agent": "Joint Meeting",
        "action": "Internal strategy meeting",
        "detail": meeting_notes,
    }

    print("[Joint Meeting] " + meeting_notes.replace("\n", " | "))

    return {
        "joint_decision": meeting_notes,
        "agent_log": [log_entry],
        "proposal_path": state.get("proposal_path", ""),
        "followup_email": state.get("followup_email", ""),
        "script": state.get("script", ""),
        "lead_info": state.get("lead_info", {}),
        "lead_score": state.get("lead_score", 0),
    }
