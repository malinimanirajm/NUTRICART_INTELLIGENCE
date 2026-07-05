from app.agents.base import BaseAgent

from agents.nutrition.service import NutritionService


class NutritionAgent(BaseAgent):

    def __init__(self):

        self.service = NutritionService()

    @property
    def name(self):

        return "nutrition"

    async def run(self, state: dict) -> dict:

        report = self.service.monthly_summary(

            customer_id=state["customer_id"]

        )

        state.setdefault("agent_results", {})

        state["agent_results"]["nutrition"] = report

        return state