"""
guardrails/models.py
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class GuardResult:

    passed: bool

    message: str = ""

    data: dict = field(default_factory=dict)


@dataclass
class AuditRecord:

    timestamp: datetime

    customer_id: str

    query: str

    planner_output: list[str]

    executed_agents: list[str]

    execution_time: float

    success: bool