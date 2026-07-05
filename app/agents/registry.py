from app.agents.memory_agent import MemoryAgent
from app.agents.recommendation_agent import RecommendationAgent
from app.agents.search_agent import SearchAgent
from app.agents.nutrition_agent import NutritionAgent
from app.agents.order_agent import OrderAgent
from app.models import AgentType


class AgentRegistry:
    """
    Registry of all available agents.
    """

    def __init__(self):

        self._agents = {
            AgentType.SEARCH: SearchAgent(),
            AgentType.MEMORY: MemoryAgent(),
            AgentType.RECOMMENDATION: RecommendationAgent(),
            AgentType.NUTRITION: NutritionAgent(),  # Placeholder for NutritionAgent
            AgentType.ORDER: OrderAgent(),  # Placeholder for OrderAgent
        }

    def get(self, agent_type: AgentType):

        return self._agents.get(agent_type)


registry = AgentRegistry()