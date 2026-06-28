from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage

# Stage names for progress callbacks
STAGE_MAP = {
    "web_search_tool": "searching",
    "web_crawl_tool": "crawling",
    "analyze_lead_tool": "analyzing",
    "generate_email_tool": "email",
    "generate_script_tool": "script",
    "generate_proposal_tool": "proposal",
}
MSG_MAP = {
    "web_search_tool": "正在搜索企业信息...",
    "web_crawl_tool": "正在爬取官网内容...",
    "analyze_lead_tool": "正在评估线索...",
    "generate_email_tool": "正在生成跟进邮件...",
    "generate_script_tool": "正在生成通话话术...",
    "generate_proposal_tool": "正在生成销售提案...",
}


def run_agent(system_prompt, tools, user_message, temperature=0.1, max_turns=10, progress_callback=None):
    from langchain.chat_models import init_chat_model
    """Run an agent with tool-calling capability.
    The LLM decides which tools to call. Returns final text + tool results.
    progress_callback: optional callable(stage, message) for streaming UI updates.
    """
    llm = init_chat_model("deepseek-chat", temperature=temperature)
    llm_with_tools = llm.bind_tools(tools)

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message),
    ]
    tool_results = {}

    for _ in range(max_turns):
        if progress_callback:
            progress_callback("thinking", "AI 正在分析...")

        response = llm_with_tools.invoke(messages)
        if not response.tool_calls:
            if progress_callback:
                progress_callback("done", "分析完成")
            return {"output": response.content or "", "tool_results": tool_results}

        messages.append(response)
        for tc in response.tool_calls:
            name = tc["name"]
            args = tc["args"]
            matched = None
            for t in tools:
                if t.name == name:
                    matched = t
                    break
            if matched is None:
                messages.append(ToolMessage(content="not available", tool_call_id=tc["id"]))
                continue

            stage = STAGE_MAP.get(name, "tool")
            msg = MSG_MAP.get(name, "正在执行 " + name + "...")
            if progress_callback:
                progress_callback(stage, msg)

            result_str = str(matched.invoke(args))
            messages.append(ToolMessage(content=result_str, tool_call_id=tc["id"]))
            tool_results.setdefault(name, []).append(result_str)

    if progress_callback:
        progress_callback("done", "分析完成")

    return {"output": "Max turns reached.", "tool_results": tool_results}
