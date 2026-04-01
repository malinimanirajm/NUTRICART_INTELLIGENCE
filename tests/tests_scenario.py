import pytest
import asyncio
from src.rag.graph import app_graph

@pytest.mark.asyncio
async def test_scenario_1_discovery():
    """Test finding high protein, low sugar snacks."""
    state = {
        "question": "Find snacks with more than 10g protein and less than 5g sugar",
        "configurable": {"thread_id": "test_1"}
    }
    result = await app_graph.ainvoke(state)
    assert result["mode"] == "discovery"
    assert "protein" in result["answer"].lower()
    print("\n✅ Scenario 1 (Discovery) Passed")

@pytest.mark.asyncio
async def test_scenario_2_analytics():
    """Test monthly consumption summary for a specific user."""
    state = {
        "question": "Show my monthly protein summary for C001",
        "configurable": {"thread_id": "test_2"}
    }
    result = await app_graph.ainvoke(state)
    assert result["mode"] == "consumption"
    assert "2024-" in result["answer"]  # Check for date formatting
    print("✅ Scenario 2 (Analytics) Passed")

@pytest.mark.asyncio
async def test_scenario_3_comparison():
    """Test the delta calculation between two periods."""
    state = {
        "question": "Compare C001 protein in 2024-09 vs 2024-12",
        "configurable": {"thread_id": "test_3"}
    }
    result = await app_graph.ainvoke(state)
    assert result["mode"] == "comparison"
    assert "vs" in result["answer"]
    assert "📈" in result["answer"] or "📉" in result["answer"]
    print("✅ Scenario 3 (Comparison) Passed")

@pytest.mark.asyncio
async def test_scenario_4_coaching():
    state = {"question": "Why is my protein lower in Dec than Sept for C001?"}
    result = await app_graph.ainvoke(state)
    assert "Coach's Insight" in result["answer"]
    assert len(result.get("recommendations", [])) > 0
    print("✅ Scenario 4 (Coaching) Passed")

if __name__ == "__main__":
    asyncio.run(test_scenario_1_discovery())
    asyncio.run(test_scenario_2_analytics())
    asyncio.run(test_scenario_3_comparison())
    asyncio.run(test_scenario_4_coaching())