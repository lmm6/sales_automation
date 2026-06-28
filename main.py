from core.agent.loader import load_agent_profile
from graph.workflow import build_sales_graph

# 加载两个智能体
lead_agent = load_agent_profile("profiles/lead_master.yaml")
proposal_agent = load_agent_profile("profiles/proposal_crafter.yaml")

# 构建流程
graph = build_sales_graph()

# 执行
if __name__ == "__main__":
    result = graph.invoke({
        "lead_agent": lead_agent,
        "proposal_agent": proposal_agent,
        "company_url": "https://openai.com",
        "lead_info": {},
        "lead_score": 0,
        "proposal_path": "",
        "followup_email": "",
        "script": "",
        "messages": []
    })

    print("✅ 流程完成")
    print("线索评分：", result["lead_score"])
    print("提案路径：", result["proposal_path"])
    print("跟进邮件：", result["followup_email"])