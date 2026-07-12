from langchain_groq import ChatGroq
from ai_companion.settings import settings
from pydantic import BaseModel
from typing import Literal
from ai_companion.lab.text_to_speech import TextToSpeech


def get_chat_model():
    model = settings.TEXT_MODEL_NAME
    api_key = settings.GROQ_API_KEY
    return ChatGroq(model=model, api_key=api_key)

    
class RouterResponse(BaseModel):
    response_type: Literal["conversation", "image", "audio"]


def get_router_chain():
    model = get_chat_model()
    return model.with_structured_output(RouterResponse)

def get_text_to_speech_module() -> TextToSpeech:
    return TextToSpeech()
    