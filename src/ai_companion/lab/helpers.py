from langchain_groq import ChatGroq
from ai_companion.settings import settings

def get_chat_model():
    model = settings.TEXT_MODEL_NAME
    api_key = settings.GROQ_API_KEY
    return ChatGroq(model=model, api_key=api_key)

    
