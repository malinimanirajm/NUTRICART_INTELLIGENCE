"""
memory/confidence_engine.py
"""

from memory.memory_types.semantic_memory import SemanticMemory


class ConfidenceEngine:
    """
    Updates confidence scores for semantic memories.
    """

    # -----------------------------------------------------

    def update(
        self,
        memories,
        episodes,
    ):

        if memories is None:
            return None

        # Handle a single SemanticMemory object
        if not isinstance(memories, list):
            memories = [memories]

        total = max(len(episodes), 1)

        for memory in memories:

            matches = 0

            for episode in episodes:

                payload = getattr(
                    episode.event,
                    "payload",
                    {},
                )

                key = getattr(
                    memory,
                    "key",
                    None,
                )

                value = getattr(
                    memory,
                    "value",
                    None,
                )

                if key is None:
                    continue

                if payload.get(
                    key.replace("preferred_", "")
                ) == value:

                    matches += 1

            if hasattr(memory, "confidence"):
                memory.confidence = round(
                    matches / total,
                    2,
                )

        return memories

    # -----------------------------------------------------
    # Backward compatibility
    # -----------------------------------------------------

    def refresh(
        self,
        memories,
        episodes,
    ):
        return self.update(
            memories,
            episodes,
        )