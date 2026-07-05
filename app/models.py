"""
Shared models used across the Supervisor.
"""

from enum import Enum

from pydantic import BaseModel, Field


class AgentType(str, Enum):
    SEARCH = "search"
    MEMORY = "memory"
    RECOMMENDATION = "recommendation"
    NUTRITION = "nutrition"
    ORDER = "order"


class IntentType(str, Enum):
    PRODUCT_SEARCH = "product_search"
    RECOMMENDATION = "recommendation"
    NUTRITION_ANALYTICS = "nutrition_analytics"
    ORDER_HISTORY = "order_history"
    UNKNOWN = "unknown"


class ExecutionPlan(BaseModel):
    """
    Planner output.
    """

    intent: IntentType

    agents: list[AgentType] = Field(default_factory=list)