"""tests/test_profile.py"""

# Placeholder implementation.
from memory.memory_types.customer_profile import CustomerProfile


def test_profile():

    profile = CustomerProfile(

        customer_id="C001"

    )

    assert profile.customer_id == "C001"

    assert profile.semantic_count == 0