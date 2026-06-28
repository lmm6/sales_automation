import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, jsonify, send_from_directory, Response, stream_with_context
import re
import json
from dotenv import load_dotenv
load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("DEEPSEEK_API_KEY", "")
os.environ["OPENAI_API_BASE"] = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1")

from core.agent.loader import load_agent_profile
from core.tools.check_web import validate_url

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/chat/stream")
def chat_stream():
    url = request.args.get("url", "").strip()
    if not url:
        return jsonify({"error": "请提供企业网址"}), 400

    ok, err = validate_url(url)
    if not ok:
        return jsonify({"error": err}), 400

    def sse(stage, message=""):
        return "data: " + json.dumps({"stage": stage, "message": message}, ensure_ascii=False) + "\n\n"

    def generate():
        try:
            lead_agent = load_agent_profile("profiles/lead_master.yaml")
            proposal_agent = load_agent_profile("profiles/proposal_crafter.yaml")

            state = {
                "lead_agent": lead_agent,
                "proposal_agent": proposal_agent,
                "company_url": url,
                "lead_info": {},
                "lead_score": 0,
                "proposal_path": "",
                "followup_email": "",
                "script": "",
                "messages": [],
            }

            # Shared progress accumulator
            progress = {"events": []}
            def on_progress(stage, message):
                progress["events"].append((stage, message))

            # Phase 1: Lead Master
            from graph.nodes import lead_master_node, proposal_crafter_node, joint_meeting_node
            state = {**state, **lead_master_node(state, progress_callback=on_progress)}
            for st, msg in progress["events"]:
                yield sse(st, msg)
            progress["events"].clear()

            score = state.get("lead_score", 0)

            if score < 80:
                yield sse("scored", f"线索评分：{score}分，低于80分跳过提案阶段")
                result = build_result(state)
                yield "event: complete\ndata: " + json.dumps({"result": result}, ensure_ascii=False) + "\n\n"
                return

            yield sse("scored", f"线索评分：{score}分，进入提案阶段")

            # Phase 2: Proposal Crafter (with feedback loop)
            for rnd in range(4):
                state = {**state, **proposal_crafter_node(state, progress_callback=on_progress)}
                for st, msg in progress["events"]:
                    yield sse(st, msg)
                progress["events"].clear()

                if state.get("feedback_request"):
                    yield sse("researching", "正在补充调研信息...")
                    state = {**state, **lead_master_node(state, progress_callback=on_progress)}
                    for st, msg in progress["events"]:
                        yield sse(st, msg)
                    progress["events"].clear()
                else:
                    break

            # Phase 3: Joint Meeting
            yield sse("meeting", "正在召开联合会议...")
            state = {**state, **joint_meeting_node(state)}

            # Build final result
            yield "event: complete\ndata: " + json.dumps({"result": build_result(state)}, ensure_ascii=False) + "\n\n"

        except Exception as e:
            import traceback
            yield sse("error", "分析出错: " + str(e))

    return Response(stream_with_context(generate()), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

def build_result(state):
    lead = state.get("lead_info", {}) or {}
    score = state.get("lead_score", 0) or 0
    return {
        "score": score,
        "company_name": lead.get("company_name", "") or "",
        "industry": lead.get("industry", "") or "",
        "pain_points": lead.get("pain_points", "") or "",
        "suggestion": lead.get("suggestion", "") or "",
        "email": state.get("followup_email", "") or "",
        "script": state.get("script", "") or "",
        "proposal_path": state.get("proposal_path", "") or "",
    }



@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = (data.get("message") or "").strip()
    history = data.get("history", [])

    url_match = re.search(r'https?://[^\s]+', message)
    if url_match:
        url = url_match.group(0).rstrip(",.;!?)")
        return jsonify({"action": "analyze", "url": url})

    system_prompt = (
        "你是 Sales Pipeline 销售助手，帮用户分析B2B销售线索。\n"
        "当用户想分析某家公司时，引导用户提供企业官网网址。\n"
        "保持简短、友好、专业的对话风格。"
    )
    try:
        from langchain.chat_models import init_chat_model
        from langchain_core.messages import SystemMessage, HumanMessage
        llm = init_chat_model("deepseek-chat", temperature=0.7)
        msgs = [SystemMessage(content=system_prompt)]
        for h in history[-6:]:
            msgs.append(HumanMessage(content=h))
        msgs.append(HumanMessage(content=message))
        resp = llm.invoke(msgs)
        reply = resp.content.strip()
    except Exception:
        reply = "你好！请提供企业官网网址，我可以帮你评估线索价值并生成销售方案。"

    return jsonify({"action": "chat", "reply": reply})

@app.route("/download/<path:filename>")
def download_file(filename):
    return send_from_directory(os.getcwd(), filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
