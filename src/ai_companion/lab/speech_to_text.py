from ai_companion.settings import settings
from ai_companion.lab.exceptions import SpeechToTextError
from groq import Groq

class SpeechToText:
    REQUIRED_ENV_VARS = ["GROQ_API_KEY"]

    def __init__(self):
        self._validate_env_vars()
        self._client = None

    def _validate_env_vars(self):
        missing_vars = []
        for var in self.REQUIRED_API_KEY:
            if not getattr(settings, var):
                missing_vars.append(var)
        if missing_vars:
            raise (SpeechToTextError(f"Missing required environment variables: {', '.join(missing_vars)}"))
        
    @property
    def client(self):
        if self._client is None:
            self._client = Groq(api_key=settings.GROQ_API_KEY)
        return self._client
            
