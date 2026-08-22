import base64
import os
from functools import lru_cache
from typing import List, Optional

from langchain_core.messages import BaseMessage
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from together import Together

from ai_companion.core.exceptions import TextToImageError
from ai_companion.core.prompts import IMAGE_ENHANCEMENT_PROMPT, IMAGE_SCENARIO_PROMPT
from ai_companion.settings import settings


class ScenarioPrompt(BaseModel):
    narrative: str = Field(..., description="First-person narrative describing the imagined scene")
    image_prompt: str = Field(..., description="Detailed visual prompt for image generation")


class EnhancedPrompt(BaseModel):
    content: str = Field(..., description="Enhanced image-generation prompt")


class TextToImage:
    """Together AI FLUX text-to-image generation for Ava's image workflow."""

    REQUIRED_ENV_VARS = ["GROQ_API_KEY", "TOGETHER_API_KEY"]
    MAX_PROMPT_LENGTH = 1000

    def __init__(self) -> None:
        self._validate_env_vars()
        self._together_client: Optional[Together] = None

    def _validate_env_vars(self) -> None:
        missing = [var for var in self.REQUIRED_ENV_VARS if not getattr(settings, var)]
        if missing:
            raise TextToImageError(f"Missing required environment variables: {', '.join(missing)}")

    @property
    def together_client(self) -> Together:
        if self._together_client is None:
            self._together_client = Together(api_key=settings.TOGETHER_API_KEY, timeout=30)
        return self._together_client

    async def generate_image(self, prompt: str, output_path: str = "") -> bytes:
        if not prompt.strip():
            raise TextToImageError("Prompt cannot be empty")

        if len(prompt) > self.MAX_PROMPT_LENGTH:
            raise TextToImageError(
                f"Prompt cannot be longer than {self.MAX_PROMPT_LENGTH} characters"
            )

        try:
            response = self.together_client.images.generate(
                prompt=prompt,
                model=settings.TTI_MODEL_NAME,
                width=1024,
                height=768,
                steps=4,
                n=1,
                response_format="b64_json",
            )
            image_data = base64.b64decode(response.data[0].b64_json)

            if output_path:
                parent = os.path.dirname(output_path)
                if parent:
                    os.makedirs(parent, exist_ok=True)
                with open(output_path, "wb") as file:
                    file.write(image_data)

            return image_data
        except TextToImageError:
            raise
        except Exception as e:
            raise TextToImageError(f"Failed to generate image: {str(e)}") from e

    async def create_scenario(self, chat_history: Optional[List[BaseMessage]] = None) -> ScenarioPrompt:
        if chat_history is None:
            chat_history = []

        try:
            formatted_history = "\n".join(
                f"{msg.type.title()}: {msg.content}" for msg in chat_history[-5:]
            )
            prompt = IMAGE_SCENARIO_PROMPT.format(chat_history=formatted_history)
            llm = ChatGroq(
                model=settings.TEXT_MODEL_NAME,
                api_key=settings.GROQ_API_KEY,
                temperature=0.4,
                max_retries=2,
            ).with_structured_output(ScenarioPrompt)
            return await llm.ainvoke(prompt)
        except TextToImageError:
            raise
        except Exception as e:
            raise TextToImageError(f"Failed to create scenario: {str(e)}") from e

    async def enhance_prompt(self, prompt: str) -> str:
        if not prompt.strip():
            raise TextToImageError("Prompt cannot be empty")

        try:
            llm = ChatGroq(
                model=settings.TEXT_MODEL_NAME,
                api_key=settings.GROQ_API_KEY,
                temperature=0.25,
                max_retries=2,
            ).with_structured_output(EnhancedPrompt)
            enhanced = await llm.ainvoke(
                IMAGE_ENHANCEMENT_PROMPT.format(prompt=prompt)
            )
            return enhanced.content
        except TextToImageError:
            raise
        except Exception as e:
            raise TextToImageError(f"Failed to enhance prompt: {str(e)}") from e


@lru_cache
def get_text_to_image() -> TextToImage:
    return TextToImage()
