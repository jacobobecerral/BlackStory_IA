import json
import os
from openai import AsyncOpenAI
from typing import Dict, Any
from ai_providers.base_provider import AIProvider

class OpenAIProvider(AIProvider):
    def __init__(self, model_name: str):
        super().__init__(model_name)
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def generate_text(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            **kwargs,
        )
        return response.choices[0].message.content

    async def generate_json(self, system_prompt: str, user_prompt: str, **kwargs) -> Dict[str, Any]:
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            **kwargs,
        )
        return json.loads(response.choices[0].message.content)
