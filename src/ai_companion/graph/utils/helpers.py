import re

from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq

from ai_companion.modules.image.image_to_text import ImageToText, get_image_to_text
from ai_companion.modules.image.text_to_image import TextToImage, get_text_to_image
from ai_companion.modules.speech.speech_to_text import SpeechToText, get_speech_to_text
from ai_companion.modules.speech.text_to_speech import TextToSpeech, get_text_to_speech
from ai_companion.settings import settings


def get_chat_model(temperature: float = 0.7) -> ChatGroq:
    return ChatGroq(
        model=settings.TEXT_MODEL_NAME,
        api_key=settings.GROQ_API_KEY,
        temperature=temperature,
    )


def get_text_to_speech_module() -> TextToSpeech:
    return get_text_to_speech()


def get_text_to_image_module() -> TextToImage:
    return get_text_to_image()


def get_image_to_text_module() -> ImageToText:
    return get_image_to_text()


def get_speech_to_text_module() -> SpeechToText:
    return get_speech_to_text()


def remove_asterisk_content(text: str) -> str:
    """Strip asterisk-wrapped action text (e.g. *smiles*) before display/TTS."""
    return re.sub(r"\*.*?\*", "", text).strip()


class AsteriskRemovalParser(StrOutputParser):
    """LangChain parser that removes asterisk actions from model output."""

    def parse(self, text: str) -> str:
        return remove_asterisk_content(super().parse(text))
