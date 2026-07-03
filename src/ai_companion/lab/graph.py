from langgraph.graph import StateGraph, START, END

from langchain_core.messages import AIMessage
from ai_companion.lab.state import LabState

def echo_node(state:  LabState):
    last = state["messages"][-1]
    return {"messages":[AIMessage(content=f"echo:{last.content}")]}

graph_builder = StateGraph(LabState)
graph_builder.add_node("echo_node", echo_node)
graph_builder.add_edge(START, "echo_node")
graph_builder.add_edge("echo_node", END)
graph = graph_builder.compile()
