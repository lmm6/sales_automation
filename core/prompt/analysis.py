# core/prompt/analysis.py
ANALYSIS_PROMPT = '你是专业B2B销售线索评分专家，根据企业信息给出 0-100 分评分。\n\n评分维度：\n- 企业规模（1-20分）\n- 行业匹配度（1-20分）\n- 潜在需求强度（1-25分）\n- 预算可能性（1-15分）\n- 决策周期（1-10分）\n- 信息完整度（1-10分）\n\n企业信息：\n公司名称：{company_name}\n搜索数据：{search_data}\n官网内容：{crawl_data}\n\n输出格式必须是严格JSON（不要添加任何额外文字、注释）：\n{{\n    "score": 分数,\n    "reason": "详细评分理由",\n    "dimensions": {{\n        "需求匹配度": 分值,\n        "预算能力": 分值,\n        "决策人级别": 分值,\n        "紧急程度": 分值\n    }},\n    "company_size": "规模描述（如：中型企业/500-1000人）",\n    "company_name": "公司真实名称（如：字节跳动/百度）",\n    "industry": "所属行业（如：新零售/人工智能）",\n    "pain_points": "客户核心痛点（1-3条）",\n    "suggestion": "具体跟进建议（如：优先推荐XX方案，重点沟通预算周期）"\n}}\n'

def format_analysis_prompt(company_name, search_data, crawl_data):
    """格式化提示词，填充企业信息"""
    return ANALYSIS_PROMPT.format(
        company_name=company_name,
        search_data=search_data if search_data else "无",
        crawl_data=crawl_data if crawl_data else "无"
    )

EMAIL_PROMPT = '你是一位资深B2B销售专家。请为以下B2B客户撰写一封专业、简洁的跟进邮件。\n\n企业：{company_name}\n行业：{industry}\n核心痛点：{pain_points}\n跟进建议：{suggestion}\n\n要求：专业简洁的商务语气，包含具体价值主张，不超过300字。只输出邮件正文。\n'

SCRIPT_PROMPT = '你是一位资深B2B电话销售专家。请为以下B2B客户撰写一通电话销售话术。\n\n企业：{company_name}\n行业：{industry}\n核心痛点：{pain_points}\n跟进建议：{suggestion}\n\n要求：包含开场白、需求探询、价值陈述、邀约下一步，对话式，不超过300字。只输出话术正文。\n'

JOINT_MEETING_PROMPT = '''你是一个B2B销售团队的内部会议记录员。现在Lead Master和Proposal Crafter正在开会讨论复杂线索的处理策略。
企业：{company_name}
行业：{industry}
线索评分：{score}
核心痛点：{pain_points}
提案路径：{proposal_path}

请模拟两位代理的讨论过程，包括：
1. Lead Master汇报线索调研结果
2. Proposal Crafter提出建议
3. 联合决定
4. 双方签署

输出格式：
=== MEETING NOTES ===
[Agent 1]: ...
[Agent 2]: ...
=== JOINT DECISION ===
...
=== SIGNATURE ===
Lead Master: ...
Proposal Crafter: ...
 '''
def format_email_prompt(company_name, industry, pain_points, suggestion):
    return EMAIL_PROMPT.format(
        company_name=company_name or "客户",
        industry=industry or "",
        pain_points=pain_points or "",
        suggestion=suggestion or ""
    )

def format_script_prompt(company_name, industry, pain_points, suggestion):
    return SCRIPT_PROMPT.format(
        company_name=company_name or "客户",
        industry=industry or "",
        pain_points=pain_points or "",
        suggestion=suggestion or ""
    )


def format_joint_meeting(company_name, industry, score, pain_points, proposal_path):
    return JOINT_MEETING_PROMPT.format(
        company_name=company_name,
        industry=industry,
        score=score,
        pain_points=pain_points,
        proposal_path=proposal_path
    )
