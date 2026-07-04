from langchain_core.messages import SystemMessage
from ai_companion.lab.helpers import get_chat_model
from ai_companion.lab.state import LabState

SYSTEM_PROMPT = """ you are an ai companion that helps the user with their tasks."""

async def conversation_node(state: LabState):
    model = get_chat_model()
    response = await model.ainvoke([SystemMessage(content = SYSTEM_PROMPT)] +state["messages"])
    return {"messages": [response]}
