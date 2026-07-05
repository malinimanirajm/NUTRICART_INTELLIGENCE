"""
guardrails/execution_guard.py
"""

from guardrails.models import GuardResult


class ExecutionGuard:

    MAX_AGENTS = 5

    def validate(
        self,
        agents: list[str],
    ) -> GuardResult:

        if len(agents) == 0:

            return GuardResult(

                False,

                "Planner selected no agents.",

            )

        if len(agents) > self.MAX_AGENTS:

            return GuardResult(

                False,

                "Too many agents selected.",

            )

        return GuardResult(True)