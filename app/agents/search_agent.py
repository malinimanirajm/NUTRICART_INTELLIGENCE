from app.agents.base import BaseAgent

from agents.search.service import SearchService


class SearchAgent(BaseAgent):

    def __init__(self):

        self.service = SearchService()

    @property
    def name(self) -> str:

        return "search"

    async def run(self, state: dict) -> dict:

        result = self.service.search(

            customer_id=state["customer_id"],

            query=state["query"],

        )

        state.setdefault("agent_results", {})

        state["agent_results"]["search"] = result

        return state