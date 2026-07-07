from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file = ".env", extra = "ignore")
    GROQ_API_KEY: str
    TEXT_MODEL_NAME: str = "llama-3.3-70b-versatile"
    QDRANT_URL: str
    QDRANT_API_KEY : str
settings = Settings()