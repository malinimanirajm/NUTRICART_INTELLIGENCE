"""
Base Agent

All agents inherit from this class.

Every agent must implement:
    - name
    - run()
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseAgent(ABC):
    """
    Abstract base class for all agents.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Unique name of the agent.
        """
        raise NotImplementedError

    @abstractmethod
    async def run(
        self,
        state: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Execute the agent.

        Args:
            state: Shared workflow state.

        Returns:
            Updated workflow state.
        """
        raise NotImplementedError