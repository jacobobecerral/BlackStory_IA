import json
import google.generativeai as genai
import os
from typing import Dict, Any
from ai_providers.base_provider import AIProvider

class GeminiProvider(AIProvider):
    def __init__(self, model_name: str):
        super().__init__(model_name)
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.client = genai.GenerativeModel(model_name)

    async def generate_text(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        # Gemini's API doesn't directly support a 'system' role in the same way as OpenAI or Ollama.
        # The system prompt needs to be incorporated into the user prompt or as a preamble.
        # For simplicity, we'll prepend the system prompt to the user prompt.
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        response = await self.client.generate_content_async(
            full_prompt,
            generation_config=kwargs.get('generation_config', {}),
            safety_settings=kwargs.get('safety_settings', {}),
        )
        return response.text

    async def generate_json(self, system_prompt: str, user_prompt: str, **kwargs) -> Dict[str, Any]:
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        response = await self.client.generate_content_async(
            full_prompt,
            generation_config=kwargs.get('generation_config', {}),
            safety_settings=kwargs.get('safety_settings', {}),
        )
        # Attempt to parse the response as JSON. Gemini might not strictly adhere to JSON format
        # if not explicitly prompted for it, so robust parsing is needed.
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            # If direct parsing fails, try to extract JSON from a larger text block
            # This is a common workaround for models that don't strictly output JSON
            import re
            json_match = re.search(r'```json\n(.*)\n```', response.text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            raise ValueError(f"Could not parse JSON from Gemini response: {response.text}")
