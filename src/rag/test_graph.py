import asyncio
from src.rag.graph import app_graph

async def test_run():
    # 1. Define a mock input
    inputs = {
        "question": "What high protein snacks can I eat? (less than 5g sugar)",
        "customer_id": "C001" # Ensure this ID is in your nutricart_vault.db
    }
    
    # 2. Config for LangGraph (thread_id is required for checkpointing)
    config = {"configurable": {"thread_id": "test_session_1"}}

    print("🚀 Starting Graph Execution...\n")
    
    # 3. Stream the graph updates
    async for event in app_graph.astream(inputs, config=config):
        for node_name, state_update in event.items():
            print(f"📍 Node: {node_name}")
            
            # Check specific outputs we added
            if "customer_id" in state_update:
                print(f"   🆔 ID Processed: {state_update['customer_id']}")
            
            if "customer_contact" in state_update:
                print(f"   📞 Contact Found: {state_update['customer_contact']}")
                
            if "safety_status" in state_update:
                print(f"   🛡️ Safety Status: {state_update['safety_status']}")
                
            if "answer" in state_update:
                print(f"   📝 Final Answer: {state_update['answer'][:100]}...")

if __name__ == "__main__":
    asyncio.run(test_run())