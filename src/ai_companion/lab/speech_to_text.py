from functools import lru_cache
from typing import Optional

from groq import AsyncGroq

from ai_companion.lab.exceptions import SpeechToTextError
from ai_companion.settings import settings


class SpeechToText:
    """Groq Whisper speech-to-text wrapper for incoming audio messages."""

    REQUIRED_ENV_VARS = ["GROQ_API_KEY"]

    def __init__(self) -> None:
        self._validate_env_vars()
        self._client: Optional[AsyncGroq] = None

    def _validate_env_vars(self) -> None:
        missing_vars = [var for var in self.REQUIRED_ENV_VARS if not getattr(settings, var)]
        if missing_vars:
            raise SpeechToTextError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )

    @property
    def client(self) -> AsyncGroq:
        if self._client is None:
            self._client = AsyncGroq(api_key=settings.GROQ_API_KEY, timeout=30)
        return self._client

    async def transcribe(self, audio_data: bytes) -> str:
        """Transcribe WAV audio bytes with Groq's Whisper model."""
        if not audio_data:
            raise SpeechToTextError("Audio data cannot be empty")

        try:
            transcription = await self.client.audio.transcriptions.create(
                file=("audio.wav", audio_data, "audio/wav"),
                model=settings.STT_MODEL_NAME,
                language="en",
                response_format="json",
            )
            text = transcription.text.strip()
            if not text:
                raise SpeechToTextError("Transcription result is empty")
            return text
        except SpeechToTextError:
            raise
        except Exception as e:
            raise SpeechToTextError(f"Speech-to-text conversion failed: {str(e)}") from e


@lru_cache
def get_speech_to_text() -> SpeechToText:
    return SpeechToText()
