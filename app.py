import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, jsonify, send_from_directory
from dotenv import load_dotenv
load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("DEEPSEEK_API_KEY", "")
os.environ["OPENAI_API_BASE"] = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1")

from core.agent.loader import load_agent_profile
from core.tools.toolkit import generate_email, generate_script
from core.tools.check_web import validate_url
from graph.workflow import build_sales_graph

app = Flask(__name__)

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_API_URL = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    company_url = (data.get("url") or "").strip()
    if not company_url:
        return jsonify({"success": False, "error": "请输入企业URL"}), 400
    ok, err = validate_url(company_url)
    if not ok:
        return jsonify({'success': False, 'error': err}), 400

    try:
        lead_agent = load_agent_profile("profiles/lead_master.yaml")
        proposal_agent = load_agent_profile("profiles/proposal_crafter.yaml")

        graph = build_sales_graph()
        result = graph.invoke({
            "lead_agent": lead_agent,
            "proposal_agent": proposal_agent,
            "company_url": company_url,
            "lead_info": {},
            "lead_score": 0,
            "proposal_path": "",
            "followup_email": "",
            "script": "",
            "messages": [],
        })

        lead_info = result.get("lead_info", {}) or {}
        score = result.get("lead_score", 0) or 0
        company_name = lead_info.get("company_name", "") or ""
        industry = lead_info.get("industry", "") or ""
        pain_points = lead_info.get("pain_points", "") or ""
        suggestion = lead_info.get("suggestion", "") or ""

        email_text = result.get("followup_email", "") or ""
        script_text = result.get("script", "") or ""

        if score >= 70 and (not email_text or len(email_text) < 20):
            email_text = generate_email({
                "company_name": company_name,
                "industry": industry,
                "pain_points": pain_points,
                "suggestion": suggestion
            }) or email_text

        if score >= 70 and (not script_text or len(script_text) < 20):
            script_text = generate_script({
                "company_name": company_name,
                "industry": industry,
                "pain_points": pain_points,
                "suggestion": suggestion
            }) or script_text
        proposal_path = result.get("proposal_path", "") or ""
        if score >= 70 and proposal_path:
            os.makedirs("proposals", exist_ok=True)
            try:
                with open(proposal_path, "w", encoding="utf-8") as f:
                    f.write("# 销售提案 - " + company_name + "\n\n")
                    f.write("**企业**：" + company_name + "\n")
                    f.write("**行业**：" + industry + "\n")
                    f.write("**核心痛点**：" + pain_points + "\n")
                    f.write("**跟进建议**：" + suggestion + "\n\n")
                    f.write("---\n\n## 方案概述\n\n")
                    f.write("针对" + company_name + "在" + industry + "行业的业务需求，我们建议以下解决方案：\n\n")
                    f.write("1. 需求分析阶段：深入了解当前业务流程与技术栈\n")
                    f.write("2. 方案设计阶段：定制化解决方案，对齐核心痛点\n")
                    f.write("3. 实施交付阶段：分阶段部署，确保平稳过渡\n")
                    f.write("4. 持续优化阶段：数据驱动迭代，持续提升ROI\n\n---\n\n")
                    f.write("*本提案由 Sales Automation Pipeline 自动生成*\n")
            except Exception:
                proposal_path = ""

        return jsonify({
            "success": True,
            "score": score,
            "company_name": company_name,
            "industry": industry,
            "pain_points": pain_points,
            "suggestion": suggestion,
            "email": email_text,
            "script": script_text,
            "proposal_path": proposal_path,
        })

    except Exception as e:
        import traceback
        return jsonify({"success": False, "error": str(e), "detail": traceback.format_exc()}), 500

@app.route("/download/<path:filename>")
def download_file(filename):
    return send_from_directory(os.getcwd(), filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
