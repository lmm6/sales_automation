import yaml
from core.agent.schema import AgentProfile

def load_agent_profile(path: str) -> AgentProfile:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return AgentProfile(**data)