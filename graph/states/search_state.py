from dataclasses import dataclass, field
from typing import List, Optional

from agents.search.filters import SearchFilters


@dataclass
class SearchState:

    customer_id: str
    query: str

    normalized_query: str | None = None
    semantic_query: str | None = None

    filters: SearchFilters | None = None
    weaviate_filter = None

    products: list[dict] = field(default_factory=list)

    validation_errors: list[str] = field(default_factory=list)

    status: str = "pending"

    message: str | None = None

    execution_time_ms: float | None = None