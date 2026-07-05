from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import uuid4

from memory.memory_types.base_memory import BaseMemory


# ==========================================================
# Semantic Memory Type
# ==========================================================

class SemanticType(str, Enum):

    CATEGORY = "category"

    BRAND = "brand"

    PRODUCT = "product"

    NUTRITION = "nutrition"

    DIET = "diet"

    SHOPPING = "shopping"

    GOAL = "goal"

    BEHAVIOUR = "behaviour"

    CUSTOM = "custom"


# ==========================================================
# Semantic Memory
# ==========================================================

@dataclass(slots=True)
class SemanticMemory(BaseMemory):
    """
    Represents long-term learned knowledge.
    """

    memory_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    customer_id: str = ""

    semantic_type: SemanticType = SemanticType.CUSTOM

    key: str = ""

    value: object = None

    fact: str = ""

    confidence: float = 0.50

    importance: float = 0.50

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )

    last_verified: datetime = field(
        default_factory=datetime.utcnow
    )

    supporting_events: list[str] = field(
        default_factory=list
    )

    access_count: int = 0

    metadata: dict = field(
        default_factory=dict
    )


        # =====================================================
    # Verification
    # =====================================================

    def verify(self):

        self.last_verified = datetime.utcnow()

    # -----------------------------------------------------

    def increase_confidence(
        self,
        amount: float = 0.05,
    ):

        self.confidence = min(
            1.0,
            self.confidence + amount,
        )

        self.verify()

    # -----------------------------------------------------

    def decrease_confidence(
        self,
        amount: float = 0.05,
    ):

        self.confidence = max(
            0.0,
            self.confidence - amount,
        )

        self.verify()

    
        # =====================================================
    # Supporting Events
    # =====================================================

    def add_supporting_event(
        self,
        event_id: str,
    ):

        if event_id not in self.supporting_events:

            self.supporting_events.append(
                event_id
            )

    # -----------------------------------------------------

    def remove_supporting_event(
        self,
        event_id: str,
    ):

        if event_id in self.supporting_events:

            self.supporting_events.remove(
                event_id
            )

    # -----------------------------------------------------

    def support_count(self) -> int:

        return len(
            self.supporting_events
        )
    

        # =====================================================
    # Access
    # =====================================================

    def accessed(self):

        self.access_count += 1

    # -----------------------------------------------------

    @property
    def verified(self) -> bool:

        return self.confidence >= 0.80
    

        # =====================================================
    # Factory Methods
    # =====================================================

    @classmethod
    def category(
        cls,
        customer_id: str,
        category: str,
        confidence: float,
    ) -> "SemanticMemory":

        return cls(

            customer_id=customer_id,

            semantic_type=SemanticType.CATEGORY,

            key="preferred_category",

            value=category,

            fact=f"Customer prefers {category}",

            confidence=confidence,

        )

    # -----------------------------------------------------

    @classmethod
    def brand(
        cls,
        customer_id: str,
        brand: str,
        confidence: float,
    ) -> "SemanticMemory":

        return cls(

            customer_id=customer_id,

            semantic_type=SemanticType.BRAND,

            key="preferred_brand",

            value=brand,

            fact=f"Customer prefers {brand}",

            confidence=confidence,

        )

    # -----------------------------------------------------

    @classmethod
    def nutrition(
        cls,
        customer_id: str,
        nutrient: str,
        value: float,
        confidence: float,
    ) -> "SemanticMemory":

        return cls(

            customer_id=customer_id,

            semantic_type=SemanticType.NUTRITION,

            key=f"preferred_{nutrient}",

            value=value,

            fact=f"Customer usually prefers {value} {nutrient}",

            confidence=confidence,

        )

    # -----------------------------------------------------

    @classmethod
    def preference(
        cls,
        customer_id: str,
        preference: str,
        confidence: float,
    ) -> "SemanticMemory":

        return cls(

            customer_id=customer_id,

            semantic_type=SemanticType.DIET,

            key=preference,

            value=True,

            fact=f"Customer prefers {preference.replace('_',' ')}",

            confidence=confidence,

        )
    

        # =====================================================
    # Merge
    # =====================================================

    def merge(
        self,
        other: "SemanticMemory",
    ):
        """
        Merge another semantic memory into this one.
        """

        if self.key != other.key:

            raise ValueError(

                "Cannot merge memories with different keys."

            )

        self.confidence = max(

            self.confidence,

            other.confidence,

        )

        self.importance = max(

            self.importance,

            other.importance,

        )

        self.supporting_events = list({

            *self.supporting_events,

            *other.supporting_events,

        })

        self.metadata.update(

            other.metadata

        )

        self.last_verified = datetime.utcnow()


    
        # =====================================================
    # Confidence Decay
    # =====================================================

    def decay(
        self,
        amount: float = 0.02,
    ):
        """
        Reduce confidence over time.
        """

        self.confidence = max(

            0.0,

            self.confidence - amount,

        )

    # -----------------------------------------------------

    @property
    def expired(self) -> bool:
        """
        Whether the semantic memory
        needs revalidation.
        """

        return (

            datetime.utcnow()

            -

            self.last_verified

        ).days > 180
    



    # =====================================================
    # Serialization
    # =====================================================

    def to_dict(self) -> dict:

        return {

            "memory_id": self.memory_id,

            "customer_id": self.customer_id,

            "semantic_type": (
                self.semantic_type.value
                if hasattr(self.semantic_type, "value")
                else self.semantic_type
            ),

            "key": self.key,

            "value": self.value,

            "fact": self.fact,

            "confidence": self.confidence,

            "importance": self.importance,

            "created_at": (
                self.created_at.isoformat()
                if hasattr(self.created_at, "isoformat")
                else self.created_at
            ),

            "last_verified": (
                self.last_verified.isoformat()
                if hasattr(self.last_verified, "isoformat")
                else self.last_verified
            ),

            "supporting_events": self.supporting_events,

            "access_count": self.access_count,

            "metadata": self.metadata,

        }
    


        # =====================================================
    # Statistics
    # =====================================================

    def statistics(self) -> dict:

        return {

            "type": self.semantic_type.value,

            "confidence": self.confidence,

            "importance": self.importance,

            "supporting_events": len(

                self.supporting_events

            ),

            "verified": self.verified,

            "expired": self.expired,

            "access_count": self.access_count,

        }
    


        # =====================================================
    # Tags
    # =====================================================

    def add_tag(
        self,
        tag: str,
    ):
        """
        Add a tag to this semantic memory.
        """

        tags = self.metadata.setdefault(
            "tags",
            []
        )

        tag = tag.strip().lower()

        if tag and tag not in tags:

            tags.append(tag)

    # -----------------------------------------------------

    def remove_tag(
        self,
        tag: str,
    ):

        tags = self.metadata.get(
            "tags",
            []
        )

        tag = tag.strip().lower()

        if tag in tags:

            tags.remove(tag)

    # -----------------------------------------------------

    def tags(self) -> list[str]:

        return self.metadata.get(
            "tags",
            []
        )

    # =====================================================
    # Metadata Helpers
    # =====================================================

    def set_metadata(
        self,
        key: str,
        value,
    ):

        self.metadata[key] = value

    # -----------------------------------------------------

    def get_metadata(
        self,
        key: str,
        default=None,
    ):

        return self.metadata.get(
            key,
            default,
        )

    # =====================================================
    # Clone
    # =====================================================

    def clone(self) -> "SemanticMemory":
        """
        Create a copy of this semantic memory.
        """

        clone = SemanticMemory(

            memory_id=self.memory_id,

            customer_id=self.customer_id,

            semantic_type=self.semantic_type,

            key=self.key,

            value=self.value,

            fact=self.fact,

            confidence=self.confidence,

            importance=self.importance,

            created_at=self.created_at,

            last_verified=self.last_verified,

            supporting_events=self.supporting_events.copy(),

            access_count=self.access_count,

            metadata=self.metadata.copy(),

        )

        return clone

    # =====================================================
    # Equality
    # =====================================================

    def __eq__(
        self,
        other,
    ):

        if not isinstance(
            other,
            SemanticMemory,
        ):

            return False

        return self.memory_id == other.memory_id

    # -----------------------------------------------------

    def __hash__(self):

        return hash(
            self.memory_id
        )

    # =====================================================
    # Python Helpers
    # =====================================================

    def __repr__(self):

        return (

            f"SemanticMemory("

            f"id='{self.memory_id}', "

            f"customer='{self.customer_id}', "

            f"key='{self.key}', "

            f"value='{self.value}', "

            f"confidence={self.confidence:.2f})"

        )
    
    # ==========================================================
# Public Exports
# ==========================================================

__all__ = [

    "SemanticType",

    "SemanticMemory",

]