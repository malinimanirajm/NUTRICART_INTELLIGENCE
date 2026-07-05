"""tests/fixtures.py"""

# Placeholder implementation.
import pytest

from memory.memory_types.working_memory import WorkingMemory


@pytest.fixture
def customer_id():
    return "C001"


@pytest.fixture
def working_memory(customer_id):
    return WorkingMemory(customer_id=customer_id)