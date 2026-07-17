from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file = ".env", extra = "ignore")
    GROQ_API_KEY: str
    TEXT_MODEL_NAME: str = "llama-3.3-70b-versatile"
    QDRANT_URL: str
    QDRANT_API_KEY : str
    SMALL_TEXT_MODEL_NAME: str = "llama-3.1-8b-instant"
    ELEVENLABS_API_KEY: str
    ELEVENLABS_VOICE_ID: str
    TTS_MODEL_NAME: str = "eleven_flash_v2_5"
    TOGETHER_API_KEY: str
    TTI_MODEL_NAME: str = "black-forest-labs/FLUX.1-schnell"
    TOTAL_MESSAGES_SUMMARY_TRIGGER : int = 20
    TOTAL_MESSAGES_AFTER_SUMMARY : int = 5
    ITT_MODEL_NAME: str = "meta-llama/llama-4-scout-17b-16e-instruct"
    
settings = Settings()