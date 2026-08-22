from typing_extensions import Literal

from langgraph.graph import END

from ai_companion.graph.state import AICompanionState
from ai_companion.settings import settings


def should_summarize_conversation(
    state: AICompanionState,
) -> Literal["summarize_conversation_node", "__end__"]:
    if len(state["messages"]) > settings.TOTAL_MESSAGES_SUMMARY_TRIGGER:
        return "summarize_conversation_node"
    return END


def select_workflow(
    state: AICompanionState,
) -> Literal["conversation_node", "image_node", "audio_node"]:
    workflow = state.get("workflow", "conversation")
    if workflow == "image":
        return "image_node"
    if workflow == "audio":
        return "audio_node"
    return "conversation_node"
