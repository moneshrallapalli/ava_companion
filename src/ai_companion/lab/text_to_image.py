from typing import Optional
from together import Together
from ai_companion.settings import settings
from ai_companion.lab.exceptions import TextToImageError

class TextToImage:
    REQUIRED_ENV_VARS = ["GROQ_API_KEY","TOGETHER_API_KEY"]
    def __init__(self):
        self._validate_env_vars()
        self._together_client = None
    
    def _validate_env_vars(self):
        missing_vars = []
        for var in self.REQUIRED_ENV_VARS:
            if not getattr(settings,var):
                missing_vars.append(var)
        if missing_vars:
            raise TextToImageError(f"Missing required environment variables: {', '.join(missing_vars)}")

    @property
    def together_client(self) -> Together:
        if self._together_client is None:
            self._together_client = Together(api_key = settings.TOGETHER_API_KEY, timeout = 10)
        return self._together_client

