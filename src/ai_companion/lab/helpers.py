import re

from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from pydantic import BaseModel
from typing import Literal

from ai_companion.settings import settings
from ai_companion.lab.image_to_text import get_image_to_text
from ai_companion.lab.text_to_image import get_text_to_image
from ai_companion.lab.text_to_speech import get_text_to_speech


def remove_asterisk_content(text: str) -> str:
    """Strip asterisk-wrapped action text (e.g. *smiles*) before TTS."""
    return re.sub(r"\*.*?\*", "", text).strip()

def get_chat_model():
    model = settings.TEXT_MODEL_NAME
    api_key = settings.GROQ_API_KEY
    return ChatGroq(model=model, api_key=api_key)

    
class RouterResponse(BaseModel):
    response_type: Literal["conversation", "image", "audio"]


def get_router_chain():
    model = get_chat_model()
    return model.with_structured_output(RouterResponse)

def get_text_to_speech_module():
    return get_text_to_speech()


class AsteriskRemovalParser(StrOutputParser):
    """LangChain parser that removes asterisk actions from model output."""

    def parse(self, text: str) -> str:
        return remove_asterisk_content(super().parse(text))


def get_text_to_image_module():
    return get_text_to_image()


def get_image_to_text_module():
    return get_image_to_text()