"""tests/test_semantic.py"""

# Placeholder implementation.
from memory.memory_types.semantic_memory import SemanticMemory


def test_semantic_creation():

    memory = SemanticMemory(

        customer_id="C001",

        key="preferred_category",

        value="Beverages",

    )

    assert memory.customer_id == "C001"

    assert memory.key == "preferred_category"
