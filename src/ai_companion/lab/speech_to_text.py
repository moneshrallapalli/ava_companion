from ai_companion.settings import settings
from ai_companion.lab.exceptions import SpeechToTextError
from groq import Groq
import os
import tempfile


class SpeechToText:
    REQUIRED_ENV_VARS = ["GROQ_API_KEY"]

    def __init__(self):
        self._validate_env_vars()
        self._client = None

    def _validate_env_vars(self):
        missing_vars = []
        for var in self.REQUIRED_ENV_VARS:
            if not getattr(settings, var):
                missing_vars.append(var)
        if missing_vars:
            raise (SpeechToTextError(f"Missing required environment variables: {', '.join(missing_vars)}"))
        
    @property
    def client(self):
        if self._client is None:
            self._client = Groq(api_key=settings.GROQ_API_KEY)
        return self._client
    
    async def transcribe(self, audio_data: bytes) -> str:
        if not audio_data:
            raise SpeechToTextError("Audio data cannot be empty")

        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name

            try:
                with open(temp_file_path, "rb") as audio_file:
                    transcription = self.client.audio.transcriptions.create(
                        file=audio_file,
                        model="whisper-large-v3-turbo",
                        language="en",
                        response_format="text",
                    )

                if not transcription:
                    raise SpeechToTextError("Transcription result is empty")

                return transcription

            finally:
                os.unlink(temp_file_path)

        except SpeechToTextError:
            raise
        except Exception as e:
            raise SpeechToTextError(f"Speech-to-text conversion failed: {str(e)}") from e
