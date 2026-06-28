import json
import os

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from core.prompt.analysis import (
    ANALYSIS_PROMPT,
    format_analysis_prompt,
    format_email_prompt,
    format_script_prompt,
)

load_dotenv()

def web_search(query: str):
    try:
        import tavily
        tavily_client = tavily.TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        response = tavily_client.search(
            query=query,
            search_depth="advanced",
            max_results=5
        )
        results = []
        for item in response["results"]:
            results.append({
                "title": item["title"],
                "url": item["url"],
                "content": item["content"]
            })
        return results
    except Exception as e:
        return f"搜索失败：{str(e)}"

def web_crawl(url: str):
    """真实抓取官网信息"""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        text = soup.get_text(strip=True)[:8000]
        return text
    except:
        return "无法抓取"

def analysis(company_name, search_data, crawl_data):
    from langchain.chat_models import init_chat_model
    llm = init_chat_model(model="deepseek-chat", temperature=0.1)
    """修复：正确填充 prompt 模板 → LLM 评分"""
    prompt = ANALYSIS_PROMPT.format(
        company_name=company_name,
        search_data=json.dumps(search_data, ensure_ascii=False) if search_data else "无",
        crawl_data=str(crawl_data)[:2000] if crawl_data else "无",
    )
    try:
        resp = llm.invoke([{"role": "system", "content": prompt},
                           {"role": "user", "content": "请分析以上企业信息并返回 JSON 评分结果"}])
        text = resp.content.strip()
        text = text.split("```json")[-1].split("```")[0].strip() if "```" in text else text
        return json.loads(text)
    except Exception as e:
        return {"score": 0, "reason": str(e), "dimensions": {}}

def generate_proposal(lead: dict):
    os.makedirs("proposals", exist_ok=True)
    path = f"proposals/{lead.get('company_name','unknown')}.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# 销售提案 - {lead.get('company_name','')}\n\n"
                f"**行业**：{lead.get('industry','')}\n"
                f"**痛点**：{lead.get('pain_points','')}\n"
                f"**建议**：{lead.get('suggestion','')}\n")
    return path

def generate_email(lead):
    try:
        from langchain.chat_models import init_chat_model
        llm = init_chat_model(model="deepseek-chat", temperature=0.1)
        return llm.invoke([
            {"role": "system", "content": format_email_prompt(lead.get("company_name",""), lead.get("industry",""), lead.get("pain_points",""), lead.get("suggestion",""))},
            {"role": "user", "content":
            f"写一封 B2B 跟进邮件给 {lead.get('company_name','')}，痛点：{lead.get('pain_points','')}，只输出正文"}]).content.strip()
    except:
        return f"尊敬的{lead.get('company_name','客户')}，您好！..."

def generate_script(lead):
    try:
        from langchain.chat_models import init_chat_model
        llm = init_chat_model(model="deepseek-chat", temperature=0.1)
        return llm.invoke([
            {"role": "system", "content": format_script_prompt(lead.get("company_name",""), lead.get("industry",""), lead.get("pain_points",""), lead.get("suggestion",""))},
            {"role": "user", "content":
            f"写一通电话销售话术给 {lead.get('company_name','')}，痛点：{lead.get('pain_points','')}，只输出话术"}]).content.strip()
    except:
        return "您好，我是 XX 公司销售代表..."



from langchain_core.tools import tool





@tool

def web_search_tool(query: str) -> str:

    "Search the web for company information."

    result = web_search(query)

    return json.dumps(result, ensure_ascii=False) if isinstance(result, list) else str(result)





@tool

def web_crawl_tool(url: str) -> str:

    "Crawl a company website to extract content."

    return str(web_crawl(url))





@tool

def analyze_lead_tool(company_name: str, search_data: str, crawl_data: str) -> str:

    "Analyze and score a B2B lead."

    result = analysis(company_name, search_data, crawl_data)

    return json.dumps(result, ensure_ascii=False)





@tool

def generate_email_tool(company_name: str, industry: str, pain_points: str, suggestion: str) -> str:

    "Generate a follow-up email for a lead."

    lead = {

        "company_name": company_name,

        "industry": industry,

        "pain_points": pain_points,

        "suggestion": suggestion,

    }

    return generate_email(lead)





@tool

def generate_script_tool(company_name: str, industry: str, pain_points: str, suggestion: str) -> str:

    "Generate a sales call script for a lead."

    lead = {

        "company_name": company_name,

        "industry": industry,

        "pain_points": pain_points,

        "suggestion": suggestion,

    }

    return generate_script(lead)





@tool

def generate_proposal_tool(company_name: str, industry: str, pain_points: str, suggestion: str) -> str:

    "Generate a sales proposal document for a lead."

    lead = {

        "company_name": company_name,

        "industry": industry,

        "pain_points": pain_points,

        "suggestion": suggestion,

    }

    return generate_proposal(lead)

