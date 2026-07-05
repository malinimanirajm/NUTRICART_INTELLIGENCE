from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from memory.memory_types.episodic_memory import EpisodicMemory
from memory.memory_types.preference_memory import PreferenceMemory
from memory.memory_types.semantic_memory import SemanticMemory
from memory.memory_types.working_memory import WorkingMemory
from memory.memory_types.base_memory import BaseMemory


# ==========================================================
# Customer Profile
# ==========================================================

@dataclass(slots=True)
class CustomerProfile(BaseMemory):
    """
    Unified customer profile used by
    search, recommendation and memory.
    """

    customer_id: str

    name: str | None = None

    email: str | None = None

    working_memory: WorkingMemory | None = None

    preference_memory: PreferenceMemory | None = None

    semantic_memories: list[SemanticMemory] = field(
        default_factory=list
    )

    episodic_memories: list[EpisodicMemory] = field(
        default_factory=list
    )

    recommendation_history: list[str] = field(
        default_factory=list
    )

    feedback_history: list[str] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )

    updated_at: datetime = field(
        default_factory=datetime.utcnow
    )


        # =====================================================
    # Semantic Memory
    # =====================================================

    def add_semantic_memory(
        self,
        memory: SemanticMemory,
    ):

        self.semantic_memories.append(
            memory
        )

        self.updated_at = datetime.utcnow()

    # -----------------------------------------------------

    def semantic_by_key(
        self,
        key: str,
    ) -> list[SemanticMemory]:

        return [

            memory

            for memory in self.semantic_memories

            if memory.key == key

        ]

    # -----------------------------------------------------

    def clear_semantic(self):

        self.semantic_memories.clear()

        self.updated_at = datetime.utcnow()

    # =====================================================
    # Episodic Memory
    # =====================================================

    def add_episode(
        self,
        episode: EpisodicMemory,
    ):

        self.episodic_memories.append(
            episode
        )

        self.updated_at = datetime.utcnow()

    # -----------------------------------------------------

    def recent_episodes(
        self,
        limit: int = 20,
    ) -> list[EpisodicMemory]:

        episodes = sorted(

            self.episodic_memories,

            key=lambda e: e.timestamp,

            reverse=True,

        )

        return episodes[:limit]

    # -----------------------------------------------------

    def clear_episodes(self):

        self.episodic_memories.clear()

        self.updated_at = datetime.utcnow()

        # =====================================================
    # Recommendation History
    # =====================================================

    def add_recommendation(
        self,
        recommendation_id: str,
    ):

        self.recommendation_history.append(
            recommendation_id
        )

        self.updated_at = datetime.utcnow()

    # -----------------------------------------------------

    def add_feedback(
        self,
        feedback: str,
    ):

        self.feedback_history.append(
            feedback
        )

        self.updated_at = datetime.utcnow()

    

        # =====================================================
    # Customer Statistics
    # =====================================================

    def statistics(self) -> dict:
        """
        Overall customer statistics.
        """

        return {

            "customer_id": self.customer_id,

            "semantic_memories": len(
                self.semantic_memories
            ),

            "episodic_memories": len(
                self.episodic_memories
            ),

            "recommendations": len(
                self.recommendation_history
            ),

            "feedback": len(
                self.feedback_history
            ),

            "has_working_memory": (
                self.working_memory is not None
            ),

            "has_preference_memory": (
                self.preference_memory is not None
            ),

        }

    # =====================================================
    # Nutrition Profile
    # =====================================================

    def nutrition_profile(self) -> dict:
        """
        Return learned nutrition preferences.
        """

        if self.preference_memory is None:

            return {}

        return self.preference_memory.nutrition_preferences.copy()

    # =====================================================
    # Shopping Profile
    # =====================================================

    def shopping_profile(self) -> dict:
        """
        Return shopping preferences.
        """

        if self.preference_memory is None:

            return {}

        return {

            "categories":
                self.preference_memory.preferred_categories,

            "brands":
                self.preference_memory.preferred_brands,

            "products":
                self.preference_memory.preferred_products,

            "shopping":
                self.preference_memory.shopping_preferences,

        }
    

        # =====================================================
    # Profile Builder
    # =====================================================

    @classmethod
    def build(
        cls,
        customer_id: str,
        working_memory: WorkingMemory | None,
        preference_memory: PreferenceMemory | None,
        semantic_memories: list[SemanticMemory],
        episodic_memories: list[EpisodicMemory],
    ) -> "CustomerProfile":

        return cls(

            customer_id=customer_id,

            working_memory=working_memory,

            preference_memory=preference_memory,

            semantic_memories=semantic_memories,

            episodic_memories=episodic_memories,

        )
    

        # =====================================================
    # Merge
    # =====================================================

    def merge(
        self,
        other: "CustomerProfile",
    ):
        """
        Merge another customer profile.
        """

        self.semantic_memories.extend(
            other.semantic_memories
        )

        self.episodic_memories.extend(
            other.episodic_memories
        )

        self.recommendation_history.extend(
            other.recommendation_history
        )

        self.feedback_history.extend(
            other.feedback_history
        )

        self.metadata.update(
            other.metadata
        )

        if other.preference_memory:

            self.preference_memory = other.preference_memory

        if other.working_memory:

            self.working_memory = other.working_memory

        self.updated_at = datetime.utcnow()


        # =====================================================
    # Serialization
    # =====================================================

    def to_dict(self):

        return {

            "customer_id": self.customer_id,

            "name": self.name,

            "email": self.email,

            "working_memory":

                self.working_memory.to_dict()

                if self.working_memory

                else None,

            "preference_memory":

                self.preference_memory.to_dict()

                if self.preference_memory

                else None,

            "semantic_memories":[

                memory.to_dict()

                for memory in self.semantic_memories

            ],

            "episodic_memories":[

                episode.to_dict()

                for episode in self.episodic_memories

            ],

            "recommendation_history":

                self.recommendation_history,

            "feedback_history":

                self.feedback_history,

            "metadata":

                self.metadata,

            "created_at": (
                self.created_at.isoformat()
                if hasattr(self.created_at, "isoformat")
                else self.created_at
            ),

            "updated_at": (
                self.updated_at.isoformat()
                if hasattr(self.updated_at, "isoformat")
                else self.updated_at
            ),

        }
    

        # =====================================================
    # Clone
    # =====================================================

    def clone(self) -> "CustomerProfile":
        """
        Create a deep copy of the profile.
        """

        return CustomerProfile(

            customer_id=self.customer_id,

            name=self.name,

            email=self.email,

            working_memory=(
                self.working_memory.clone()
                if self.working_memory
                else None
            ),

            preference_memory=(
                self.preference_memory.clone()
                if self.preference_memory
                else None
            ),

            semantic_memories=[
                memory.clone()
                for memory in self.semantic_memories
            ],

            episodic_memories=[
                episode
                for episode in self.episodic_memories
            ],

            recommendation_history=self.recommendation_history.copy(),

            feedback_history=self.feedback_history.copy(),

            metadata=self.metadata.copy(),

            created_at=self.created_at,

            updated_at=self.updated_at,

        )

    # =====================================================
    # Validation
    # =====================================================

    def validate(self) -> bool:
        """
        Validate the customer profile.
        """

        if not self.customer_id:
            return False

        if (
            self.preference_memory
            and not self.preference_memory.validate()
        ):
            return False

        return True

    # =====================================================
    # Memory Counts
    # =====================================================

    @property
    def semantic_count(self) -> int:

        return len(self.semantic_memories)

    @property
    def episodic_count(self) -> int:

        return len(self.episodic_memories)

    @property
    def recommendation_count(self) -> int:

        return len(self.recommendation_history)

    # =====================================================
    # Equality
    # =====================================================

    def __eq__(
        self,
        other,
    ):

        if not isinstance(
            other,
            CustomerProfile,
        ):
            return False

        return self.customer_id == other.customer_id

    # -----------------------------------------------------

    def __hash__(self):

        return hash(
            self.customer_id
        )

    # =====================================================
    # Python Helpers
    # =====================================================

    def __len__(self):

        return (

            len(self.semantic_memories)

            +

            len(self.episodic_memories)

        )

    # -----------------------------------------------------

    def __repr__(self):

        return (

            f"CustomerProfile("

            f"customer_id='{self.customer_id}', "

            f"semantic={len(self.semantic_memories)}, "

            f"episodic={len(self.episodic_memories)}, "

            f"recommendations={len(self.recommendation_history)})"

        )


# ==========================================================
# Public Exports
# ==========================================================

__all__ = [

    "CustomerProfile",

]