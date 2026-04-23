# src/rag/security.py
import re

def is_prompt_injection(text: str) -> bool:
    patterns = [r"ignore previous instructions", r"system prompt", r"developer mode"]
    return any(re.search(p, text.lower()) for p in patterns)

def is_off_topic(text: str) -> bool:
    # Logic to ensure query is about food/nutrition
    pass