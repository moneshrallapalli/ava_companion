from langgraph.graph import StateGraph, START, END

from langchain_core.messages import AIMessage
from ai_companion.lab.state import LabState
from ai_companion.lab.nodes import conversation_node


def echo_node(state:  LabState):
    last = state["messages"][-1]
    return {"messages":[AIMessage(content=f"echo:{last.content}")]}

graph_builder = StateGraph(LabState)
graph_builder.add_node("conversational_node", conversation_node)
graph_builder.add_edge(START, "conversational_node")
graph_builder.add_edge("conversational_node", END)
graph = graph_builder.compile()
