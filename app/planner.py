"""
Rule-based Planner.

Responsible only for deciding which agents should execute.
"""

from app.models import (
    AgentType,
    ExecutionPlan,
    IntentType,
)


class Planner:

    def create_plan(self, query: str) -> ExecutionPlan:

        query = query.lower()

        #
        # Recommendation
        #

        if "recommend" in query:

            return ExecutionPlan(
                intent=IntentType.RECOMMENDATION,
                agents=[
                    AgentType.MEMORY,
                    AgentType.SEARCH,
                    AgentType.RECOMMENDATION,
                ],
            )

        #
        # Nutrition analytics
        #

        if (
            "month" in query
            or "week" in query
            or "year" in query
            or "consumed" in query
        ):

            return ExecutionPlan(
                intent=IntentType.NUTRITION_ANALYTICS,
                agents=[
                    AgentType.MEMORY,
                    AgentType.NUTRITION,
                ],
            )

        #
        # Order history
        #

        if (
            "order" in query
            or "purchased" in query
            or "bought" in query
        ):

            return ExecutionPlan(
                intent=IntentType.ORDER_HISTORY,
                agents=[
                    AgentType.ORDER,
                ],
            )

        #
        # Default
        #

        return ExecutionPlan(
            intent=IntentType.PRODUCT_SEARCH,
            agents=[
                AgentType.SEARCH,
            ],
        )


planner = Planner()