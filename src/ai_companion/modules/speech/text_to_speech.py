from functools import lru_cache
from typing import Optional
import re

from elevenlabs import ElevenLabs, VoiceSettings

from ai_companion.core.exceptions import TextToSpeechError
from ai_companion.settings import settings


class TextToSpeech:
    """ElevenLabs text-to-speech wrapper for Ava's audio responses."""

    REQUIRED_ENV_VARS = ["ELEVENLABS_API_KEY", "ELEVENLABS_VOICE_ID"]
    MAX_TEXT_LENGTH = 5000

    def __init__(self) -> None:
        self._validate_env_vars()
        self._client: Optional[ElevenLabs] = None

    def _validate_env_vars(self) -> None:
        missing = [var for var in self.REQUIRED_ENV_VARS if not getattr(settings, var)]
        if missing:
            raise TextToSpeechError(f"Missing required environment variables: {', '.join(missing)}")

    @property
    def client(self) -> ElevenLabs:
        if self._client is None:
            self._client = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY, timeout=10)
        return self._client

    def prepare_speech_text(self, text: str) -> str:
        """Clean LLM output for speech (strip *actions* and whitespace)."""
        return re.sub(r"\*.*?\*", "", text).strip()

    async def synthesize(self, text: str) -> bytes:
        speech_text = self.prepare_speech_text(text)
        if not speech_text:
            raise TextToSpeechError("Text to synthesize cannot be empty")

        if len(speech_text) > self.MAX_TEXT_LENGTH:
            raise TextToSpeechError(
                f"Text to synthesize cannot be longer than {self.MAX_TEXT_LENGTH} characters"
            )

        try:
            audio_generator = self.client.text_to_speech.convert(
                voice_id=settings.ELEVENLABS_VOICE_ID,
                text=speech_text,
                model_id=settings.TTS_MODEL_NAME,
                voice_settings=VoiceSettings(stability=0.5, similarity_boost=0.5),
            )
            audio_bytes = b"".join(audio_generator)
            if not audio_bytes:
                raise TextToSpeechError("Generated audio is empty")
            return audio_bytes
        except TextToSpeechError:
            raise
        except Exception as e:
            raise TextToSpeechError(f"Text-to-speech conversion failed: {str(e)}") from e


@lru_cache
def get_text_to_speech() -> TextToSpeech:
    return TextToSpeech()
