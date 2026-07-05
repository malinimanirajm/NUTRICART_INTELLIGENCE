"""
memory/semantic_builder.py
"""

from collections import Counter

from memory.memory_types.semantic_memory import SemanticMemory


class SemanticBuilder:
    """
    Builds semantic memories from episodic memories.
    """

    def __init__(
        self,
        min_occurrences: int = 3,
    ):
        self.min_occurrences = min_occurrences

    # =====================================================

    def build(
        self,
        customer_id: str,
        episodes: list,
    ) -> list[SemanticMemory]:

        memories = []

        memories.extend(
            self._learn(
                customer_id,
                episodes,
                field="category",
                key="preferred_category",
            )
        )

        memories.extend(
            self._learn(
                customer_id,
                episodes,
                field="brand",
                key="preferred_brand",
            )
        )

        return memories

    # =====================================================

    def _learn(
        self,
        customer_id: str,
        episodes: list,
        field: str,
        key: str,
    ) -> list[SemanticMemory]:

        counter = Counter()

        for episode in episodes:

            payload = getattr(
                episode.event,
                "payload",
                {},
            )

            value = payload.get(field)

            if value:
                counter[value] += 1

        print("=" * 80)
        print(f"Learning {key}")
        print(counter)
        print("=" * 80)

        memories = []

        if not counter:
            return memories

        #
        # Relative confidence
        #
        highest = max(counter.values())

        for value, count in counter.items():

            if count < self.min_occurrences:
                continue

            confidence = round(
                count / highest,
                2,
            )

            memories.append(
                SemanticMemory(
                    customer_id=customer_id,
                    key=key,
                    value=value,
                    confidence=confidence,
                )
            )

        print("=" * 80)
        print("Semantic Memories")

        for memory in memories:
            print(memory)

        print("=" * 80)

        return memories