from typing import Optional
from together import Together
from ai_companion.settings import settings
from ai_companion.lab.exceptions import TextToImageError
import base64
import os
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from ai_companion.lab.prompts import IMAGE_SCENARIO_PROMPT

class ScenarioPrompt(BaseModel):
    narrative: str = Field(..., description = "a detailed narrative describing the scene to be depicted in the image")
    image_prompt: str = Field(..., description = "a concise and specific prompt for the image generation that captures the key elements and style desired")


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


    async def generate_image(self, prompt:str, output_path: str = "") -> bytes:
        if not prompt.strip():
            raise TextToImageError("Prompt cannot be empty")
        if len(prompt) > 1000:
            raise TextToImageError("Prompt cannot be longer than 1000 characters")
        try:
            response = self.together_client.images.generate(
                prompt = prompt, 
                model= settings.TTI_MODEL_NAME, 
                width = 1024, 
                height = 768, 
                steps = 4, 
                n = 1, 
                response_format = "b64_json")
            image_data = base64.b64decode(response.data[0].b64_json)
            if output_path:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, "wb") as f:
                    f.write(image_data)
            return image_data
        except Exception as e:
            raise TextToImageError(f"Failed to generate image: {str(e)}") from e

    async def create_scenario(self, chat_history: list = None) -> ScenarioPrompt:
        try:
            formatted_history = "\n".join(
                [f"{msg.type.title()}: {msg.content}" for msg in chat_history[-5:]]
            )
            prompt = IMAGE_SCENARIO_PROMPT.format(chat_history = formatted_history)
            llm = ChatGroq(model = settings.TEXT_MODEL_NAME, api_key = settings.GROQ_API_KEY, temperature = 0.5, max_retries = 3).with_structured_output(ScenarioPrompt)
            scenario = await llm.ainvoke(prompt)
            return scenario
        except Exception as e:
            raise TextToImageError(f"Failed to create scenario: {str(e)}") from e
