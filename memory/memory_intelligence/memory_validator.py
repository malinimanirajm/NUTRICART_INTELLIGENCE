"""
memory/memory_validator.py
"""

from memory.memory_types.semantic_memory import SemanticMemory


class MemoryValidator:
    """
    Validates semantic memories.
    Removes invalid or duplicate memories only.
    """

    def validate(
        self,
        memories: list[SemanticMemory],
    ) -> list[SemanticMemory]:

        if memories is None:
            return []

        validated = []
        seen = set()

        for memory in memories:

            if memory is None:
                continue

            if memory.customer_id is None:
                continue

            if not memory.key:
                continue

            if memory.value is None:
                continue

            identity = (
                memory.customer_id,
                memory.key,
                str(memory.value),
            )

            if identity in seen:
                continue

            seen.add(identity)
            validated.append(memory)

        return validated