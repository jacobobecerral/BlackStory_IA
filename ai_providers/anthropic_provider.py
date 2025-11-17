import json
import os
from anthropic import AsyncAnthropic
from typing import Dict, Any
from ai_providers.base_provider import AIProvider

class AnthropicProvider(AIProvider):
    def __init__(self, model_name: str):
        super().__init__(model_name)
        self.client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    async def generate_text(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        response = await self.client.messages.create(
            model=self.model_name,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt},
            ],
            **kwargs,
        )
        return response.content[0].text

    async def generate_json(self, system_prompt: str, user_prompt: str, **kwargs) -> Dict[str, Any]:
        # Anthropic does not have a direct JSON mode like OpenAI.
        # We need to instruct the model to output JSON and then parse it.
        user_prompt_with_json_instruction = f"{user_prompt}\n\nResponde SOLAMENTE con un objeto JSON válido."
        response = await self.client.messages.create(
            model=self.model_name,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt_with_json_instruction},
            ],
            **kwargs,
        )
        try:
            return json.loads(response.content[0].text)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'```json\n(.*)\n```', response.content[0].text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            raise ValueError(f"Could not parse JSON from Anthropic response: {response.content[0].text}")
