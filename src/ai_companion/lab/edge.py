from langgraph.graph import END
from ai_companion.settings import settings
from ai_companion.lab.state import LabState

def should_summarize_conversation(state:LabState):
    if len(state["messages"]) > settings.TOTAL_MESSAGES_SUMMARY_TRIGGER :
        return "summarize_conversation_node"
    else:
        return END
