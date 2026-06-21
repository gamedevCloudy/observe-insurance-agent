from langchain_core.messages import SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode

from app.agents.call_agent.memory import store
from app.agents.call_agent.prompt import SYSTEM_PROMPT
from app.agents.call_agent.tools import ALL_TOOLS
from app.llm.openrouter import get_openrouter_client


def _agent_node(state: MessagesState) -> dict:
    llm = get_openrouter_client().bind_tools(ALL_TOOLS)
    response = llm.invoke([SystemMessage(content=SYSTEM_PROMPT)] + state["messages"])
    return {"messages": [response]}


def _should_continue(state: MessagesState) -> str:
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    return END


def build_agent():
    graph = StateGraph(MessagesState)  # ty: ignore[invalid-argument-type]
    graph.add_node("agent", _agent_node)
    graph.add_node("tools", ToolNode(ALL_TOOLS))
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", _should_continue, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")
    return graph.compile(checkpointer=MemorySaver(), store=store)
