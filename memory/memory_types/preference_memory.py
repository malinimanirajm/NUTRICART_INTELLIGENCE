from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from memory.memory_types.base_memory import BaseMemory
from memory.memory_types.semantic_memory import SemanticMemory


# ==========================================================
# Preference Memory
# ==========================================================

@dataclass(slots=True)
class PreferenceMemory(BaseMemory):
    """
    Stable customer preferences derived
    from semantic memories.
    """

    customer_id: str

    preferred_categories: list[str] = field(
        default_factory=list
    )

    preferred_brands: list[str] = field(
        default_factory=list
    )

    preferred_products: list[str] = field(
        default_factory=list
    )

    dietary_preferences: list[str] = field(
        default_factory=list
    )

    nutrition_preferences: dict[str, float] = field(
        default_factory=dict
    )

    shopping_preferences: dict[str, Any] = field(
        default_factory=dict
    )

    confidence: float = 0.50

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )

    updated_at: datetime = field(
        default_factory=datetime.utcnow
    )

    source_memories: list[str] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


        # =====================================================
    # Build From Semantic Memories
    # =====================================================

    @classmethod
    def from_semantic(
        cls,
        customer_id: str,
        memories: list[SemanticMemory],
    ) -> "PreferenceMemory":

        preference = cls(
            customer_id=customer_id,
        )

        confidence = []

        for memory in memories:

            preference.source_memories.append(
                memory.memory_id
            )

            confidence.append(
                memory.confidence
            )

            if memory.key == "preferred_category":

                preference.preferred_categories.append(
                    str(memory.value)
                )

            elif memory.key == "preferred_brand":

                preference.preferred_brands.append(
                    str(memory.value)
                )

            elif memory.key == "repeat_product":

                preference.preferred_products.append(
                    str(memory.value)
                )

            elif memory.key.startswith("preferred_"):

                nutrient = memory.key.replace(
                    "preferred_",
                    "",
                )

                if nutrient in {

                    "protein",

                    "calories",

                    "fat",

                    "fiber",

                    "sugar",

                    "sodium",

                }:

                    preference.nutrition_preferences[
                        nutrient
                    ] = float(memory.value)

            elif memory.value is True:

                preference.dietary_preferences.append(
                    memory.key
                )

        if confidence:

            preference.confidence = round(
                sum(confidence) / len(confidence),
                4,
            )

        return preference
    

        # =====================================================
    # Update
    # =====================================================

    def update(self):

        self.updated_at = datetime.utcnow()

    # -----------------------------------------------------

    def add_category(
        self,
        category: str,
    ):

        if category not in self.preferred_categories:

            self.preferred_categories.append(
                category
            )

            self.update()

    # -----------------------------------------------------

    def add_brand(
        self,
        brand: str,
    ):

        if brand not in self.preferred_brands:

            self.preferred_brands.append(
                brand
            )

            self.update()

    # -----------------------------------------------------

    def add_product(
        self,
        product: str,
    ):

        if product not in self.preferred_products:

            self.preferred_products.append(
                product
            )

            self.update()

    
        # =====================================================
    # Dietary Preferences
    # =====================================================

    def add_dietary_preference(
        self,
        preference: str,
    ):

        preference = preference.strip().lower()

        if preference not in self.dietary_preferences:

            self.dietary_preferences.append(
                preference
            )

            self.update()

    # -----------------------------------------------------

    def remove_dietary_preference(
        self,
        preference: str,
    ):

        preference = preference.strip().lower()

        if preference in self.dietary_preferences:

            self.dietary_preferences.remove(
                preference
            )

            self.update()

    # =====================================================
    # Nutrition Preferences
    # =====================================================

    def set_nutrition(
        self,
        nutrient: str,
        value: float,
    ):

        self.nutrition_preferences[
            nutrient.lower()
        ] = value

        self.update()

    # -----------------------------------------------------

    def nutrition(
        self,
        nutrient: str,
        default: float | None = None,
    ):

        return self.nutrition_preferences.get(

            nutrient.lower(),

            default,

        )

    # =====================================================
    # Shopping Preferences
    # =====================================================

    def set_shopping_preference(
        self,
        key: str,
        value,
    ):

        self.shopping_preferences[key] = value

        self.update()

    # -----------------------------------------------------

    def shopping_preference(
        self,
        key: str,
        default=None,
    ):

        return self.shopping_preferences.get(

            key,

            default,

        )

    # =====================================================
    # Metadata
    # =====================================================

    def set_metadata(
        self,
        key: str,
        value,
    ):

        self.metadata[key] = value

        self.update()

    # -----------------------------------------------------

    def metadata_value(
        self,
        key: str,
        default=None,
    ):

        return self.metadata.get(

            key,

            default,

        )
    

        # =====================================================
    # Merge
    # =====================================================

    def merge(
        self,
        other: "PreferenceMemory",
    ):
        """
        Merge another preference profile.
        """

        self.preferred_categories = list({

            *self.preferred_categories,

            *other.preferred_categories,

        })

        self.preferred_brands = list({

            *self.preferred_brands,

            *other.preferred_brands,

        })

        self.preferred_products = list({

            *self.preferred_products,

            *other.preferred_products,

        })

        self.dietary_preferences = list({

            *self.dietary_preferences,

            *other.dietary_preferences,

        })

        self.nutrition_preferences.update(

            other.nutrition_preferences

        )

        self.shopping_preferences.update(

            other.shopping_preferences

        )

        self.metadata.update(

            other.metadata

        )

        self.source_memories = list({

            *self.source_memories,

            *other.source_memories,

        })

        self.confidence = max(

            self.confidence,

            other.confidence,

        )

        self.update()

    

        # =====================================================
    # Serialization
    # =====================================================

    def to_dict(self):

        return {

            "customer_id": self.customer_id,

            "preferred_categories": self.preferred_categories,

            "preferred_brands": self.preferred_brands,

            "preferred_products": self.preferred_products,

            "dietary_preferences": self.dietary_preferences,

            "nutrition_preferences": self.nutrition_preferences,

            "shopping_preferences": self.shopping_preferences,

            "confidence": self.confidence,

            "created_at": self.created_at.isoformat(),

            "updated_at": self.updated_at.isoformat(),

            "source_memories": self.source_memories,

            "metadata": self.metadata,

        }
    

        # =====================================================
    # Statistics
    # =====================================================

    def statistics(self):

        return {

            "categories": len(

                self.preferred_categories

            ),

            "brands": len(

                self.preferred_brands

            ),

            "products": len(

                self.preferred_products

            ),

            "dietary_preferences": len(

                self.dietary_preferences

            ),

            "nutrition_preferences": len(

                self.nutrition_preferences

            ),

            "shopping_preferences": len(

                self.shopping_preferences

            ),

            "source_memories": len(

                self.source_memories

            ),

            "confidence": self.confidence,

        }
    

        # =====================================================
    # Clone
    # =====================================================

    def clone(self) -> "PreferenceMemory":
        """
        Create a deep copy of this preference profile.
        """

        clone = PreferenceMemory(

            customer_id=self.customer_id,

            preferred_categories=self.preferred_categories.copy(),

            preferred_brands=self.preferred_brands.copy(),

            preferred_products=self.preferred_products.copy(),

            dietary_preferences=self.dietary_preferences.copy(),

            nutrition_preferences=self.nutrition_preferences.copy(),

            shopping_preferences=self.shopping_preferences.copy(),

            confidence=self.confidence,

            created_at=self.created_at,

            updated_at=self.updated_at,

            source_memories=self.source_memories.copy(),

            metadata=self.metadata.copy(),

        )

        return clone

    # =====================================================
    # Validation
    # =====================================================

    def validate(self) -> bool:
        """
        Validate the preference profile.
        """

        if not self.customer_id:

            return False

        if not (0.0 <= self.confidence <= 1.0):

            return False

        return True

    # =====================================================
    # Equality
    # =====================================================

    def __eq__(
        self,
        other,
    ):

        if not isinstance(
            other,
            PreferenceMemory,
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

            len(self.preferred_categories)

            +

            len(self.preferred_brands)

            +

            len(self.preferred_products)

        )

    # -----------------------------------------------------

    def __repr__(self):

        return (

            f"PreferenceMemory("

            f"customer_id='{self.customer_id}', "

            f"categories={len(self.preferred_categories)}, "

            f"brands={len(self.preferred_brands)}, "

            f"products={len(self.preferred_products)}, "

            f"confidence={self.confidence:.2f})"

        )
    

    # ==========================================================
# Public Exports
# ==========================================================

__all__ = [

    "PreferenceMemory",

]

