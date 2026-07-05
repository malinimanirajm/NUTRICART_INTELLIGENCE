from __future__ import annotations
import profile

from memory.memory_service.event_manager import EventManager, EventType
from memory.memory_service.memory_pipeline import MemoryPipeline


class MemoryService:
    """
    High-level facade for all memory operations.
    """

    def __init__(
        self,
        pipeline: MemoryPipeline | None = None,
        event_manager: EventManager | None = None,
    ):

        self.pipeline = pipeline or MemoryPipeline()

        self.event_manager = event_manager or EventManager()

    # =====================================================
    # Learning
    # =====================================================

    def learn(
        self,
        event_type: EventType,
        customer_id: str,
        **kwargs,
    ):

        episode = self.event_manager.create(

            event_type=event_type,

            customer_id=customer_id,

            **kwargs,

        )

        return self.pipeline.learn(episode)

    # =====================================================
    # Retrieval
    # =====================================================

    def retrieve(
        self,
        customer_id: str,
        query: str,
        top_k: int = 10,
    ):

        return self.pipeline.retrieve(
            customer_id,
            query,
            top_k,
        )

    # =====================================================
    # Customer Profile
    # =====================================================

    def profile(
        self,
        customer_id: str,
    ):

        return self.pipeline.profile(customer_id)
    
    

    # =====================================================
    # Recommendation Context
    # =====================================================

    def recommendation_context(
        self,
        customer_id: str,
        query: str,
    ):
        return self.pipeline.recommendation_context(
            customer_id,
            query,
        )

    # =====================================================
    # Maintenance
    # =====================================================

    def refresh(
        self,
        customer_id: str,
    ):

        return self.pipeline.refresh(customer_id)

    def reduce(
        self,
        customer_id: str,
    ):

        return self.pipeline.reduce(customer_id)
    
        # =====================================================
    # Backward Compatibility
    # =====================================================

    def get_customer_memory(
        self,
        customer_id: str,
    ):
        """
        Returns all memory required by RecommendationService.
        Works even if a customer profile has not yet been created.
        """

        profile = self.pipeline.repo.get_profile(customer_id)

        preference = self.pipeline.repo.get_preference(customer_id)

        semantic = self.pipeline.repo.get_semantic(customer_id)

        episodes = self.pipeline.repo.get_episodes(customer_id)

        return {

            "profile": profile,

            "preferences": preference,

            "semantic": semantic,

            "episodes": episodes,

        }

    # =====================================================
    # Health
    # =====================================================

    def health(self):

        return {

            "service": "healthy",

            "pipeline": self.pipeline.health(),

            "events": self.event_manager.health(),

        }

    # =====================================================
    # Convenience APIs
    # =====================================================

    def search(
        self,
        customer_id: str,
        query: str,
        filters: dict | None = None,
    ):

        return self.learn(

            EventType.SEARCH,

            customer_id,

            query=query,

            filters=filters,

        )

    def purchase(
        self,
        customer_id: str,
        product_id: str,
        quantity: int = 1,
        **payload,
    ):

        return self.learn(

            EventType.PURCHASE,

            customer_id,

            product_id=product_id,

            quantity=quantity,

            **payload,

        )

    def feedback(
        self,
        customer_id: str,
        text: str,
        sentiment: str | None = None,
    ):

        return self.learn(

            EventType.FEEDBACK,

            customer_id,

            text=text,

            sentiment=sentiment,

        )

    def rating(
        self,
        customer_id: str,
        product_id: str,
        rating: float,
    ):

        return self.learn(

            EventType.RATING,

            customer_id,

            product_id=product_id,

            rating=rating,

        )

    def __repr__(self):

        return f"MemoryService(pipeline={type(self.pipeline).__name__})"


__all__ = [
    "MemoryService",
]