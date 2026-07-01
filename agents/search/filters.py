from dataclasses import dataclass
from typing import Optional


@dataclass
class SearchFilters:

    # -----------------------------------------
    # Product Metadata
    # -----------------------------------------

    category: Optional[str] = None
    brand: Optional[str] = None

    # -----------------------------------------
    # Protein
    # -----------------------------------------

    min_protein: Optional[float] = None
    max_protein: Optional[float] = None

    protein_min_operator: str = ">="
    protein_max_operator: str = "<="

    # -----------------------------------------
    # Sugar
    # -----------------------------------------

    min_sugar: Optional[float] = None
    max_sugar: Optional[float] = None

    sugar_min_operator: str = ">="
    sugar_max_operator: str = "<="

    # -----------------------------------------
    # Calories
    # -----------------------------------------

    min_calories: Optional[float] = None
    max_calories: Optional[float] = None

    calories_min_operator: str = ">="
    calories_max_operator: str = "<="

    # -----------------------------------------
    # Fat
    # -----------------------------------------

    min_fat: Optional[float] = None
    max_fat: Optional[float] = None

    fat_min_operator: str = ">="
    fat_max_operator: str = "<="

    # -----------------------------------------
    # Fiber
    # -----------------------------------------

    min_fiber: Optional[float] = None
    max_fiber: Optional[float] = None

    fiber_min_operator: str = ">="
    fiber_max_operator: str = "<="

    # -----------------------------------------
    # Sodium
    # -----------------------------------------

    min_sodium: Optional[float] = None
    max_sodium: Optional[float] = None

    sodium_min_operator: str = ">="
    sodium_max_operator: str = "<="

    # -----------------------------------------
    # Preferences
    # -----------------------------------------

    diabetic: bool = False

    vegan: bool = False

    gluten_free: bool = False

    organic: bool = False