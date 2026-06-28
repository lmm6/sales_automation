import json
import os

import requests
import tavily
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

from core.prompt.analysis import ANALYSIS_PROMPT, format_analysis_prompt

load_dotenv()
tavily = tavily.TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# 初始化分析结果LLM
analysis_llm = init_chat_model(
    model="deepseek-chat",
    temperature=0.1
)
#暂时
llm = init_chat_model(
    model="deepseek-chat",
    temperature=0.1
)

def web_search(query: str):
    try:
        response = tavily.search(
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
    """修复：正确填充 prompt 模板 → LLM 评分"""
    prompt = ANALYSIS_PROMPT.format(
        company_name=company_name,
        search_data=json.dumps(search_data, ensure_ascii=False) if search_data else "无",
        crawl_data=str(crawl_data)[:2000] if crawl_data else "无",
    )
    try:
        resp = analysis_llm.invoke([{"role": "system", "content": prompt},
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
        return llm.invoke([{"role": "user", "content":
            f"写一封 B2B 跟进邮件给 {lead.get('company_name','')}，痛点：{lead.get('pain_points','')}，只输出正文"}]).content.strip()
    except:
        return f"尊敬的{lead.get('company_name','客户')}，您好！..."

def generate_script(lead):
    try:
        return llm.invoke([{"role": "user", "content":
            f"写一通电话销售话术给 {lead.get('company_name','')}，痛点：{lead.get('pain_points','')}，只输出话术"}]).content.strip()
    except:
        return "您好，我是 XX 公司销售代表..."

if __name__ == "__main__":
    test_lead = {
        "公司": "某新零售科技有限公司",
        "职位": "CTO",
        "需求": "需要搭建智能客服系统，对接企业微信",
        "预算": "30-50万",
        "紧急程度": "1个月内上线",
        "竞品接触": "已了解过智齿科技、网易七鱼"
    }
    base_result = analysis(test_lead)
    print("=== 评分结果 ===")
    print(json.dumps(base_result, ensure_ascii=False, indent=2))
