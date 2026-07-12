import os
from typing import Optional
from elevenlabs import ElevenLabs, VoiceSettings
from ai_companion.settings import settings
from ai_companion.lab.exceptions import TextToSpeechError

class TextToSpeech:
    REQUIRED_ENV_VARS = ["ELEVENLABS_API_KEY", "ELEVENLABS_VOICE_ID"]
    def __init__(self):
        self._validate_env_vars()
        self._client = None

    def _validate_env_vars(self):
        missing_vars = []
        for var in self.REQUIRED_ENV_VARS:
            if not getattr(settings,var):
                missing_vars.append(var)
        if missing_vars:
            raise (TextToSpeechError(f"Missing required environment variables: {', '.join(missing_vars)}"))

    @property
    def client(self) -> ElevenLabs:
        if self._client is None:
            self._client = ElevenLabs(api_key= settings.ELEVENLABS_API_KEY,timeout=10)
        return self._client








