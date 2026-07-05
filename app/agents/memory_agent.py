from app.agents.base import BaseAgent

from memory.memory_service import MemoryService


class MemoryAgent(BaseAgent):

    def __init__(self):

        self.service = MemoryService()

    @property
    def name(self):

        return "memory"

    async def run(self, state: dict) -> dict:

        result = self.service.retrieve(

            customer_id=state["customer_id"],

            query=state["query"],

        )

        state.setdefault("agent_results", {})

        state["agent_results"]["memory"] = result

        return state