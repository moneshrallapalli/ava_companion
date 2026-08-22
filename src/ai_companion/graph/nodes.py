import os
from uuid import uuid4

from langchain_core.messages import AIMessage, HumanMessage, RemoveMessage
from langchain_core.runnables import RunnableConfig

from ai_companion.graph.state import AICompanionState
from ai_companion.graph.utils.chains import get_character_response_chain, get_router_chain
from ai_companion.graph.utils.helpers import (
    get_chat_model,
    get_text_to_image_module,
    get_text_to_speech_module,
)
from ai_companion.modules.memory.long_term.memory_manager import get_memory_manager
from ai_companion.modules.schedules.context_generation import ScheduleContextGenerator
from ai_companion.settings import settings


async def router_node(state: AICompanionState):
    chain = get_router_chain()
    response = await chain.ainvoke(
        {"messages": state["messages"][-settings.ROUTER_MESSAGES_TO_ANALYZE :]}
    )
    return {"workflow": response.response_type}


def context_injection_node(state: AICompanionState):
    schedule_context = ScheduleContextGenerator.get_current_activity() or ""
    previous_activity = state.get("current_activity", "")
    apply_activity = schedule_context != previous_activity
    return {"apply_activity": apply_activity, "current_activity": schedule_context}


async def conversation_node(state: AICompanionState, config: RunnableConfig):
    chain = get_character_response_chain(state.get("summary", ""))
    response = await chain.ainvoke(
        {
            "messages": state["messages"],
            "current_activity": state.get("current_activity", "")
            or ScheduleContextGenerator.get_current_activity()
            or "",
            "memory_context": state.get("memory_context", ""),
        },
        config,
    )
    return {"messages": [AIMessage(content=response)]}


async def image_node(state: AICompanionState, config: RunnableConfig):
    chain = get_character_response_chain(state.get("summary", ""))
    text_to_image = get_text_to_image_module()

    scenario = await text_to_image.create_scenario(state["messages"][-5:])
    os.makedirs("generated_images", exist_ok=True)
    image_path = f"generated_images/image_{uuid4()}.png"
    await text_to_image.generate_image(scenario.image_prompt, image_path)

    scenario_message = HumanMessage(
        content=f"<image attached by Ava generated from prompt: {scenario.image_prompt}>"
    )
    updated_messages = state["messages"] + [scenario_message]
    response = await chain.ainvoke(
        {
            "messages": updated_messages,
            "current_activity": state.get("current_activity", "")
            or ScheduleContextGenerator.get_current_activity()
            or "",
            "memory_context": state.get("memory_context", ""),
        },
        config,
    )
    return {"messages": [AIMessage(content=response)], "image_path": image_path}


async def audio_node(state: AICompanionState, config: RunnableConfig):
    chain = get_character_response_chain(state.get("summary", ""))
    text_to_speech = get_text_to_speech_module()

    response = await chain.ainvoke(
        {
            "messages": state["messages"],
            "current_activity": state.get("current_activity", "")
            or ScheduleContextGenerator.get_current_activity()
            or "",
            "memory_context": state.get("memory_context", ""),
        },
        config,
    )
    audio_buffer = await text_to_speech.synthesize(response)
    return {"messages": [AIMessage(content=response)], "audio_buffer": audio_buffer}


async def summarize_conversation_node(state: AICompanionState):
    model = get_chat_model()
    summary = state.get("summary", "")

    if summary:
        summary_message = (
            "This is summary of the conversation to date between Ava and the user: "
            + summary
            + "\n\nExtend the summary by taking into account the new messages above:"
        )
    else:
        summary_message = (
            "Create a summary of the conversation above between Ava and the user. "
            "The summary must be a short description of the conversation so far, "
            "but that captures all the relevant information shared between Ava and the user:"
        )

    messages = state["messages"] + [HumanMessage(content=summary_message)]
    response = await model.ainvoke(messages)
    delete_messages = [
        RemoveMessage(id=m.id)
        for m in state["messages"][: -settings.TOTAL_MESSAGES_AFTER_SUMMARY]
    ]
    return {"summary": response.content, "messages": delete_messages}


async def memory_extraction_node(state: AICompanionState):
    if not state["messages"]:
        return {}
    memory_manager = get_memory_manager()
    await memory_manager.extract_and_store_memories(state["messages"][-1])
    return {}


def memory_injection_node(state: AICompanionState):
    memory_manager = get_memory_manager()
    recent_context = " ".join(m.content for m in state["messages"][-3:])
    memories = memory_manager.get_relevant_memories(recent_context)
    memory_context = memory_manager.format_memories_for_prompt(memories)
    return {"memory_context": memory_context}
