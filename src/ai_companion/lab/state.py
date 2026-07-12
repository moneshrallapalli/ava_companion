from langgraph.graph import MessagesState

class LabState(MessagesState):

    current_activity: str
    apply_activity : bool
    workflow: str
    memory_context: str
    audio_buffer: bytes
    
