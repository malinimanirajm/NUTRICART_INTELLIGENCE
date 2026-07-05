"""
LangGraph workflow for the Supervisor.

Current Flow

START
    │
    ▼
Planner
    │
    ▼
Executor
    │
    ▼
Response
    │
    ▼
END
"""

from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from app.executor import executor


class SupervisorState(TypedDict):
    """
    Shared state passed between LangGraph nodes.
    """

    customer_id: str
    query: str
    execution_plan: Any
    agent_results: dict[str, Any]
    response: dict[str, Any]


# ---------------------------------------------------------------------
# Planner Node
# ---------------------------------------------------------------------


async def planner_node(state: SupervisorState) -> SupervisorState:
    """
    Planner node.

    The planner has already created the execution plan inside the
    Supervisor.

    Later this node can enrich or validate the plan.
    """

    print("\n========== PLANNER ==========")
    print("Planner Node Executed")
    print("=============================\n")

    return state


# ---------------------------------------------------------------------
# Executor Node
# ---------------------------------------------------------------------


async def executor_node(state: SupervisorState) -> SupervisorState:
    """
    Executes all agents selected by the planner.
    """

    return await executor.execute(state)


# ---------------------------------------------------------------------
# Response Node
# ---------------------------------------------------------------------


async def response_node(state: SupervisorState) -> SupervisorState:
    """
    Build the API response.
    """

    plan = state["execution_plan"]

    state["response"] = {
        "status": "success",
        "customer_id": state["customer_id"],
        "query": state["query"],
        "intent": plan.intent.value,
        "agents": [agent.value for agent in plan.agents],
        "agent_results": state.get("agent_results", {}),
        "message": "Workflow executed successfully.",
    }

    return state


# ---------------------------------------------------------------------
# Build Graph
# ---------------------------------------------------------------------


builder = StateGraph(SupervisorState)

builder.add_node("planner", planner_node)
builder.add_node("executor", executor_node)
builder.add_node("response", response_node)

builder.add_edge(START, "planner")
builder.add_edge("planner", "executor")
builder.add_edge("executor", "response")
builder.add_edge("response", END)

graph = builder.compile()