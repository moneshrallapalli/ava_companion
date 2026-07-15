from langgraph.graph import StateGraph, START, END

from langchain_core.messages import AIMessage
from ai_companion.lab.state import LabState
from ai_companion.lab.nodes import conversation_node, context_injection_node, router_node
from ai_companion.lab.nodes import memory_extraction_node, memory_injection_node
from ai_companion.lab.nodes import audio_node, image_node, summarize_conversation_node
from ai_companion.lab.edge import should_summarize_conversation
# def echo_node(state:  LabState):
# last = state["messages"][-1]
# return {"messages":[AIMessage(content=f"echo:{last.content}")]}


def select_workflow(state):
    if state["workflow"] == "image":
        return "image_node"
    elif state["workflow"] == "audio":
        return "audio_node"
    else:
        return "conversation_node"




graph_builder = StateGraph(LabState)
graph_builder.add_node("conversation_node", conversation_node)
graph_builder.add_node("context_injection_node", context_injection_node)
graph_builder.add_node("image_node", image_node)
graph_builder.add_node("audio_node", audio_node)
graph_builder.add_node("memory_extraction_node", memory_extraction_node)
graph_builder.add_node("router_node", router_node)
graph_builder.add_node("memory_injection_node", memory_injection_node)
graph_builder.add_node("summarize_conversation_node", summarize_conversation_node)
#graph_builder.add_edge(START, "context_injection_node")
graph_builder.add_edge(START, "memory_extraction_node")
graph_builder.add_edge("memory_extraction_node", "router_node")
graph_builder.add_edge("router_node", "context_injection_node")
graph_builder.add_edge("context_injection_node", "memory_injection_node")
graph_builder.add_conditional_edges("memory_injection_node", select_workflow)
#graph_builder.add_edge("context_injection_node","conversation_node")
graph_builder.add_conditional_edges("image_node", should_summarize_conversation)
graph_builder.add_conditional_edges("audio_node", should_summarize_conversation)
graph_builder.add_conditional_edges("conversation_node", should_summarize_conversation)
graph_builder.add_edge("summarize_conversation_node", END)

graph = graph_builder.compile()




