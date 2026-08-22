import os
from base64 import b64encode
from functools import lru_cache
from typing import Optional, Union

from groq import AsyncGroq

from ai_companion.lab.exceptions import ImageToTextError
from ai_companion.settings import settings


class ImageToText:
    """Groq vision wrapper for describing user-uploaded images."""

    REQUIRED_ENV_VARS = ["GROQ_API_KEY"]
    DEFAULT_PROMPT = "Please describe what you see in this image in detail."

    def __init__(self) -> None:
        self._validate_env_vars()
        self._client: Optional[AsyncGroq] = None

    def _validate_env_vars(self) -> None:
        missing_vars = [var for var in self.REQUIRED_ENV_VARS if not getattr(settings, var)]
        if missing_vars:
            raise ImageToTextError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )

    @property
    def client(self) -> AsyncGroq:
        if self._client is None:
            self._client = AsyncGroq(api_key=settings.GROQ_API_KEY, timeout=30)
        return self._client

    def _load_image_bytes(self, image_data: Union[str, bytes]) -> bytes:
        if isinstance(image_data, str):
            if not os.path.exists(image_data):
                raise ImageToTextError(f"Image file not found: {image_data}")
            with open(image_data, "rb") as image_file:
                image_bytes = image_file.read()
        elif isinstance(image_data, bytes):
            image_bytes = image_data
        else:
            raise ImageToTextError("Invalid image data type")

        if not image_bytes:
            raise ImageToTextError("Image data cannot be empty")
        return image_bytes

    async def analyze_image(self, image_data: Union[str, bytes], prompt: str = "") -> str:
        """Analyze an image with Groq vision. Accepts a file path or raw bytes."""
        image_bytes = self._load_image_bytes(image_data)
        encoded_image = b64encode(image_bytes).decode("utf-8")
        analysis_prompt = prompt.strip() or self.DEFAULT_PROMPT

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": analysis_prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"},
                    },
                ],
            }
        ]

        try:
            response = await self.client.chat.completions.create(
                model=settings.ITT_MODEL_NAME,
                messages=messages,
                max_tokens=1000,
            )
            if not response.choices:
                raise ImageToTextError("No response received from the vision model")

            description = (response.choices[0].message.content or "").strip()
            if not description:
                raise ImageToTextError("Vision model returned an empty description")
            return description
        except ImageToTextError:
            raise
        except Exception as e:
            raise ImageToTextError(f"Failed to analyze image: {str(e)}") from e


@lru_cache
def get_image_to_text() -> ImageToText:
    return ImageToText()
