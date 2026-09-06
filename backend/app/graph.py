import logging
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from app.state import AgentState
from app.nodes import (
    understand_query_node,
    resume_node,
    social_links_node,
    contact_agent_node,
    rag_retrieval_node,
    gemini_answer_node
)

logger = logging.getLogger("neeraj_portfolio_assistant.graph")

def route_intent(state: AgentState) -> str:
    """Conditional router that determines which branch to take based on classified intent."""
    intent = state.get("intent", "portfolio_info")
    if intent == "resume":
        return "resume"
    elif intent in ["github", "kaggle", "linkedin"]:
        return "social_links"
    elif intent == "contact":
        return "contact_agent"
    else:
        return "rag_retrieval"

def build_portfolio_graph():
    """Constructs and compiles the LangGraph StateGraph workflow with in-memory checkpointer."""
    workflow = StateGraph(AgentState)

    # Register nodes
    workflow.add_node("understand_query", understand_query_node)
    workflow.add_node("resume", resume_node)
    workflow.add_node("social_links", social_links_node)
    workflow.add_node("contact_agent", contact_agent_node)
    workflow.add_node("rag_retrieval", rag_retrieval_node)
    workflow.add_node("gemini_answer", gemini_answer_node)

    # Add edges
    workflow.add_edge(START, "understand_query")

    # Conditional routing after intent classification
    workflow.add_conditional_edges(
        "understand_query",
        route_intent,
        {
            "resume": "resume",
            "social_links": "social_links",
            "contact_agent": "contact_agent",
            "rag_retrieval": "rag_retrieval"
        }
    )

    # Linear edges to termination
    workflow.add_edge("rag_retrieval", "gemini_answer")
    workflow.add_edge("gemini_answer", END)
    workflow.add_edge("resume", END)
    workflow.add_edge("social_links", END)
    workflow.add_edge("contact_agent", END)

    # In-memory thread checkpointer for stateful conversational memory without a database
    checkpointer = MemorySaver()
    app_graph = workflow.compile(checkpointer=checkpointer)
    return app_graph

portfolio_agent = build_portfolio_graph()
