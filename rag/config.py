from rag.prompts.system_prompts import SYSTEM_PROMPTS_REGISTRY
#from rag.prompts.guardrails import GUARDRAIL_PROMPTS_REGISTRY
from rag.prompts.behavioral_rules import BEHAVIOR_PROMPTS_REGISTRY

# CENTRAL PROMPT VERSION MANAGERS
ACTIVE_SYSTEM_VERSION = "v1.1.0"  # Target version tag to deploy
ACTIVE_GUARDRAIL_VERSION = "v1.0.0"
ACTIVE_BEHAVIOR_STYLE = "default"

def get_agent_prompt(agent_name: str) -> str:
    """Retrieves a system identity string stitched with dynamic tone boundaries."""
    base_prompt = SYSTEM_PROMPTS_REGISTRY[ACTIVE_SYSTEM_VERSION][agent_name]
    behavior = BEHAVIOR_PROMPTS_REGISTRY[ACTIVE_BEHAVIOR_STYLE]["tone"]
    return f"{base_prompt}\nBehavior and Persona Rule: {behavior}"

def get_guardrail_prompt(type_key: str) -> str:
    """Retrieves target structural safety parameters."""
    return GUARDRAIL_PROMPTS_REGISTRY[ACTIVE_GUARDRAIL_VERSION][type_key]