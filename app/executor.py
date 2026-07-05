from app.agents.registry import registry


class Executor:
    """
    Executes all agents selected by the planner.
    """

    async def execute(self, state: dict) -> dict:

        plan = state["execution_plan"]

        state.setdefault("agent_results", {})

        print("\n===== EXECUTOR =====")

        for agent_type in plan.agents:

            print(f"Running {agent_type.value}")

            agent = registry.get(agent_type)

            if agent is None:
                print(f"{agent_type.value} not registered")
                continue

            state = await agent.run(state)

        print("====================\n")

        return state


executor = Executor()