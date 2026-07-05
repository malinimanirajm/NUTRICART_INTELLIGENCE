"""
agents/supervisor/service.py
"""

from time import perf_counter

from agents.supervisor.planner import Planner
from agents.supervisor.router import Router

from guardrails.audit import AuditLogger
from guardrails.execution_guard import ExecutionGuard
from guardrails.input_guard import InputGuard
from guardrails.planner_guard import PlannerGuard


class SupervisorService:

    def __init__(self):

        self.planner = Planner()

        self.router = Router()

        self.input_guard = InputGuard()

        self.planner_guard = PlannerGuard()

        self.execution_guard = ExecutionGuard()

        self.audit = AuditLogger()

    # -----------------------------------------------------

    def execute(
        self,
        customer_id: str,
        query: str,
    ):

        # ==================================================
        # Input Guard
        # ==================================================

        result = self.input_guard.validate(query)

        if not result.passed:

            raise ValueError(result.message)

        start = perf_counter()

        # ==================================================
        # Planner
        # ==================================================

        planner_response = self.planner.plan(query)

        print("\nPlanner Response")
        print("=" * 80)
        print(planner_response)
        print("=" * 80)

        agents = self._extract_agents(
            planner_response
        )

        # ==================================================
        # Planner Guard
        # ==================================================

        result = self.planner_guard.validate(
            agents
        )

        if not result.passed:

            raise ValueError(result.message)

        # ==================================================
        # Execution Guard
        # ==================================================

        result = self.execution_guard.validate(
            agents
        )

        if not result.passed:

            raise ValueError(result.message)

        print("\nExecuting Agents")
        print("=" * 80)
        print(agents)
        print("=" * 80)

        # ==================================================
        # Execute
        # ==================================================

        response = self.router.execute(

            customer_id,

            query,

            agents,

        )

        elapsed = perf_counter() - start

        # ==================================================
        # Audit
        # ==================================================

        self.audit.log(

            customer_id=customer_id,

            query=query,

            planner_output=agents,

            executed_agents=agents,

            execution_time=elapsed,

            success=True,

        )

        return response

    # -----------------------------------------------------

    def _extract_agents(
        self,
        planner_output: str,
    ) -> list[str]:

        available = [

            "Search",

            "Recommendation",

            "Memory",

            "Nutrition",

            "Order",

        ]

        selected = []

        for agent in available:

            if agent.lower() in planner_output.lower():

                selected.append(agent)

        return selected

    # -----------------------------------------------------

    def audit_history(self):

        return self.audit.history()