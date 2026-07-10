from langchain_core.messages import SystemMessage
from ai_companion.lab.helpers import get_chat_model, get_router_chain
from ai_companion.lab.state import LabState
from ai_companion.lab.schedules import ScheduleContextGenerator
from ai_companion.lab.memory_manager import get_memory_manager

SYSTEM_PROMPT = """You are an AI companion that assists the user with their tasks. The current user activity is: {current_activity}. Use this information as contextual awareness to make your responses more relevant, helpful, and timely. Do not assume details beyond what the activity implies, and ask clarifying questions when needed."""
ROUTER_PROMPT ="""You are a routing classifier. Read the user's request and return exactly one of these three strings with no additional text:

- Return "image" if the user asks to see, draw, generate, create, visualize, edit, or describe an image or other visual content.
- Return "audio" if the user asks Ava to speak, say, read aloud, sing, or otherwise respond with a voice or audio output.
- Otherwise, return "conversation".

Output only one of: "image", "audio", or "conversation"."""

async def conversation_node(state: LabState):
    model = get_chat_model()
    activity = state.get("current_activity","")
    system_prompt = SYSTEM_PROMPT.format(current_activity=activity)
    response = await model.ainvoke([SystemMessage(content = system_prompt)] +state["messages"])
    return {"messages": [response]}

def context_injection_node(state: LabState):
    activity = ScheduleContextGenerator.get_current_activity()
    previous = state.get("current_activity","")
    changed = activity != previous
    return {"current_activity":activity, "apply_activity":changed}
    
async def router_node(state: LabState):
    chain = get_router_chain()
    response = await chain.ainvoke([SystemMessage(content = ROUTER_PROMPT)] + state["messages"][-5:])
    return {"workflow":response.response_type}

async def memory_extraction_node(state: Labstate):
    if not state["messages"]: return {}
    memory_manager = get_memory_manager()
    await memory_manager.extract_and_store_memories(state["messages"][-1])
    return {}

def memory_injection_nodes(state: Lastate):
    memory_manager = get_memory_manager()
    recent_context = " ".join([m.content for m in state["messages"][-3:]])
    memories = memory_manager.get_relevant_memories(recent_context)
    memory_context = memory_manager.format_memories_for_prompt(memories)
    return {"memory_context": memory_context}

