from typing import List, Optional

from pydantic import BaseModel , Field
from ai_companion.lab.vector_store import VectorStore
from ai_companion import settings
from langchain_groq import ChatGroq

class MemoryAnalysis(BaseModel):
    is_important: bool = Field(..., description = "is the message important enough to be remembered?")
    formatted_memory: Optional[str] = Field(..., description = "a concise and structured summary of the message that captures the key information and context")


class MemoryManager:
    def __init__(self):
        self.vector_store = VectorStore()
        self.llm = ChatGroq(model = settings.SMALL_TEXT_MODEL_NAME, api_key=settings.GROQ_API_KEY, temperature = 0.1, max_retries = 3).with_structured_output(MemoryAnalysis)