# core/prompt/analysis.py
ANALYSIS_PROMPT = """
你是专业B2B销售线索评分专家，根据企业信息给出 0-100 分评分。

评分维度：
- 企业规模（1-20分）
- 行业匹配度（1-20分）
- 潜在需求强度（1-25分）
- 预算可能性（1-15分）
- 决策周期（1-10分）
- 信息完整度（1-10分）

企业信息：
公司名称：{company_name}
搜索数据：{search_data}
官网内容：{crawl_data}

输出格式必须是严格JSON（不要添加任何额外文字、注释）：
{{
    "score": 分数,
    "reason": "详细评分理由",
    "dimensions": {{
        "需求匹配度": 分值,
        "预算能力": 分值,
        "决策人级别": 分值,
        "紧急程度": 分值
    }},
    "company_size": "规模描述（如：中型企业/500-1000人）",
    "industry": "所属行业（如：新零售/人工智能）",
    "pain_points": "客户核心痛点（1-3条）",
    "suggestion": "具体跟进建议（如：优先推荐XX方案，重点沟通预算周期）"
}}
"""

# 补充提示词格式化函数（方便传参）
def format_analysis_prompt(company_name, search_data, crawl_data):
    """格式化提示词，填充企业信息"""
    return ANALYSIS_PROMPT.format(
        company_name=company_name,
        search_data=search_data if search_data else "无",
        crawl_data=crawl_data if crawl_data else "无"
    )