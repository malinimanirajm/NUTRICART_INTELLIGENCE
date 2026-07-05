"""
guardrails/audit.py
"""

from datetime import datetime

from guardrails.models import AuditRecord


class AuditLogger:

    def __init__(self):

        self.records = []

    def log(

        self,

        customer_id: str,

        query: str,

        planner_output: list[str],

        executed_agents: list[str],

        execution_time: float,

        success: bool,

    ):

        self.records.append(

            AuditRecord(

                timestamp=datetime.now(),

                customer_id=customer_id,

                query=query,

                planner_output=planner_output,

                executed_agents=executed_agents,

                execution_time=execution_time,

                success=success,

            )

        )

    def history(self):

        return self.records