"""
agents/supervisor/models.py
"""

from dataclasses import dataclass, field


@dataclass
class Plan:

    query: str

    agents: list[str] = field(
        default_factory=list
    )


@dataclass
class AgentResponse:

    agent: str

    result: object