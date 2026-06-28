from core.tools.toolkit import *

def lead_master_node(state: dict):
    print("\n🔍 Lead Master 开始挖掘线索...")

    company_url = state["company_url"]
    company_name = company_url.split("//")[-1].split("/")[0]

    # 1.搜索企业信息
    search_result = web_search(f"{company_name} 公司简介 业务 规模 行业")

    # 2. 抓取官网
    crawl_result = web_crawl(company_url)

    # 3. 整合线索
    result = analysis(company_name, search_result, crawl_result)
    lead_info = {"company_name": company_name, "website": state["company_url"],
            "search_data": search_result, "crawl_data": str(crawl_result)[:1000],
            "industry": result.get("industry", ""),
            "pain_points": result.get("pain_points", ""),
            "suggestion": result.get("suggestion", "")}
    score = result.get("score", 0)

    print(f"✅ 线索挖掘完成 | 评分：{score}")
    return {
        "lead_info": lead_info,
        "lead_score": score
    }

def proposal_crafter_node(state: dict):
    print("📑 正在生成个性化销售提案...")
    lead = state["lead_info"]
    prop = generate_proposal(lead)
    email = generate_email(lead)
    script = generate_script(lead)
    print(f"✅ 完成 | 提案：{prop}")
    return {"proposal_path": prop, "followup_email": email, "script": script}
