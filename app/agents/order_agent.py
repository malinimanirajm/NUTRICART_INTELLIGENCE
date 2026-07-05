from app.agents.base import BaseAgent

from agents.order.service import OrderService


class OrderAgent(BaseAgent):

    def __init__(self):

        self.service = OrderService()

    @property
    def name(self):

        return "order"

    async def run(self, state: dict) -> dict:

        orders = self.service.monthly_orders(

            customer_id=state["customer_id"]

        )

        state.setdefault("agent_results", {})

        state["agent_results"]["order"] = orders

        return state