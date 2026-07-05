"""
guardrails/planner_guard.py
"""

from guardrails.models import GuardResult


class PlannerGuard:

    VALID_AGENTS = {

        "Search",

        "Recommendation",

        "Memory",

        "Nutrition",

        "Order",

    }

    def validate(
        self,
        agents: list[str],
    ) -> GuardResult:

        invalid = [

            agent

            for agent in agents

            if agent not in self.VALID_AGENTS

        ]

        if invalid:

            return GuardResult(

                False,

                f"Unknown agents: {invalid}",

            )

        return GuardResult(True)