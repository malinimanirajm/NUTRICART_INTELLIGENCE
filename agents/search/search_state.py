from dataclasses import dataclass, field
from typing import List, Optional

from agents.search.filters import SearchFilters


@dataclass
class SearchState:

    def trace(self):
        print("=" * 80)
        print(f"Query            : {self.query}")
        print(f"Semantic Query   : {self.semantic_query}")
        print(f"Status           : {self.status}")
        print(f"Filters          : {self.filters}")
        print(f"Validation       : {self.validation_errors}")
        print(f"Weaviate Filter  : {self.weaviate_filter}")
        print(f"Products         : {len(self.products)}")
        print(f"Execution (ms)   : {self.execution_time_ms}")
        print("=" * 80)

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

    