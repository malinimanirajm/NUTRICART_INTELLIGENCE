"""
agents/supervisor/planner.py
"""

from langchain_ollama import ChatOllama


class Planner:

    def __init__(self):

        self.llm = ChatOllama(
            model="llama3.1"
        )

    # -----------------------------------------------------

    def plan(
        self,
        query: str,
    ) -> str:

        prompt = f"""
You are an AI supervisor.

Available agents

- Search
- Recommendation
- Memory
- Nutrition
- Order

Return ONLY the required agents.

Query:

{query}
"""

        return self.llm.invoke(
            prompt
        ).content