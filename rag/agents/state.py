# src/agents/state.py
from typing import Annotated, TypedDict, List, Optional
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """Unified system data structure shared across all graph processing nodes."""
    messages: Annotated[List[AnyMessage], add_messages] # Automatically handles chat history appending
    customer_id: str                                    # Maps directly to the WhatsApp phone number
    time_frame: str                                     # Tracks context windows ('week', 'month', 'year')
    next_node: str                                      # Supervisor routing assignment target
    attached_pdf_url: Optional[str]                    # Pointer to the latest user diagnostic PDF
    attached_image_url: Optional[str]                  # Pointer to the latest macro dashboard graphic