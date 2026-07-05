from app.agents.base import BaseAgent

from agents.recommendation.service import RecommendationService


class RecommendationAgent(BaseAgent):

    def __init__(self):

        self.service = RecommendationService()

    @property
    def name(self):

        return "recommendation"

    async def run(self, state: dict) -> dict:

        result = self.service.recommend(

            customer_id=state["customer_id"],

            query=state["query"],

        )

        state.setdefault("agent_results", {})

        state["agent_results"]["recommendation"] = result

        return state