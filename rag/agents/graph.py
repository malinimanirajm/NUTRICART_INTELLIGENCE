# src/agents/graph.py
import os
import boto3
import psycopg
from psycopg.rows import dict_row
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver

from src.agents.state import AgentState
from src.agents.nodes.supervisor import supervisor_node
from src.agents.nodes.preferences import preferences_node
from src.agents.nodes.data_mining import data_mining_node

# ==========================================
# 🗺️ 1. CONDITIONAL ROUTING CONTROLLER
# ==========================================
def route_next(state: AgentState):
    """Evaluates the next node field updated by the supervisor."""
    if state["next_node"] == "preferences_agent":
        return "preferences_agent"
    elif state["next_node"] == "data_mining_agent":
        return "data_mining_agent"
    return END

# ==========================================
# 🛠️ 2. BIND WORKFLOW STRUCTURE
# ==========================================
builder = StateGraph(AgentState)

# Register nodes from external files
builder.add_node("supervisor", supervisor_node)
builder.add_node("preferences_agent", preferences_node)
builder.add_node("data_mining_agent", data_mining_node)

# Set edges and structural loops
builder.add_edge(START, "supervisor")
builder.add_conditional_edges("supervisor", route_next)
builder.add_edge("preferences_agent", "supervisor")
builder.add_edge("data_mining_agent", "supervisor")

# ==========================================
# 🔒 3. DYNAMIC IAM CHECKPOINTER CONNECTION
# ==========================================
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
DB_HOST = os.getenv("AWS_RDS_HOST")
DB_USER = os.getenv("AWS_RDS_USER", "postgres")

# Generate live token for checkpointer initialization
rds_client = boto3.client('rds', region_name=AWS_REGION)
token = rds_client.generate_db_auth_token(
    DBHostname=DB_HOST,
    Port=5432,
    DBUsername=DB_USER,
    Region=AWS_REGION
)

# Connect with parameters mandatory for PostgresSaver (autocommit and dict rows)
conn_string = f"postgresql://{DB_USER}:{token}@{DB_HOST}:5432/postgres?sslmode=require"
conn = psycopg.connect(conn_string, autocommit=True, row_factory=dict_row)

checkpointer = PostgresSaver(conn)
checkpointer.setup() # Automatically provisions checkpoint tables if missing

# Compile graph into executable runtime block
app_graph = builder.compile(checkpointer=checkpointer)