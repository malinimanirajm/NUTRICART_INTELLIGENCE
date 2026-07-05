"""tests/test_repository.py"""

# Placeholder implementation.
from memory.memory_repository.sqlite_repository import SQLiteMemoryRepository
from memory.memory_types.working_memory import WorkingMemory


def test_save_working_memory():

    repo = SQLiteMemoryRepository(":memory:")

    memory = WorkingMemory(customer_id="C001")

    repo.save_working(memory)

    result = repo.get_working("C001")

    assert result is not None
