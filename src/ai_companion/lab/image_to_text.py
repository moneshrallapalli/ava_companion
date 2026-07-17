from groq import Groq
from ai_companion.settings import settings
from ai_companion.lab.exceptions import ImageToTextError
from base64 import b64encode
import os


class ImageToText():
    REQUIRED_ENV_VARS = ["GROQ_API_KEY"]
    def __init__(self):
        self._validate_env_vars()
        self._client = None

    def _validate_env_vars(self):
        missing_vars = []
        for var in self.REQUIRED_ENV_VARS:
            if not getattr(settings,var):
                missing_vars.append(var)
        if missing_vars:
            raise ImageToTextError(f"Missing environment variables: {', '.join(missing_vars)}")

    @property
    def client(self):
        if self._client is None:
            self._client = Groq(api_key=settings.GROQ_API_KEY)
        return self._client
    
    async def analyze_image(self, image_data, prompt = "") -> str:
        try:
            if isinstance(image_data, str):
                with open(image_data, "rb") as image_file:
                    image_data = image_file.read()
            elif isinstance(image_data, bytes):
                pass
            else:
                raise ImageToTextError("Invalid image data type")
            
            if not image_data:
                raise ImageToTextError("Image data cannot be empty")
            encoded_image = b64encode(image_data).decode("utf-8")
            if not prompt:
                prompt = "Describe the image in detail"
            
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"},
                        },
                    ],
                }
            ]
            response = self.client.chat.completions.create(
                model=settings.ITT_MODEL_NAME,
                messages=messages,
                max_tokens=1000,
            )
            return response.choices[0].message.content
        except Exception as e:
            raise ImageToTextError(f"Failed to analyze image: {str(e)}") from e