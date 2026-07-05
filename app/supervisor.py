from typing import Any

from app.graph import graph
from app.planner import planner


class Supervisor:
    """
    Coordinates execution through LangGraph.
    """

    async def run(self, request: dict[str, Any]) -> dict[str, Any]:

        customer_id = request.get("customer_id")
        query = request.get("query", "")

        # Create execution plan
        plan = planner.create_plan(query)

        print("\n========== EXECUTION PLAN ==========")
        print("Intent :", plan.intent.value)
        print("Agents :", [agent.value for agent in plan.agents])
        print("====================================\n")

        state = {
            "customer_id": customer_id,
            "query": query,
            "execution_plan": plan,
            "response": {},
        }

       
        result = await graph.ainvoke(state)

        return result["response"]


supervisor = Supervisor()