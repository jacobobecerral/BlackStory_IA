import json
import ollama
from typing import Dict, Any
from ai_providers.base_provider import AIProvider

class OllamaProvider(AIProvider):
    async def generate_text(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        response = ollama.chat(
            model=self.model_name,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt},
            ],
            options=kwargs.get('options', {}),
        )
        return response['message']['content']

    async def generate_json(self, system_prompt: str, user_prompt: str, **kwargs) -> Dict[str, Any]:
        response = ollama.chat(
            model=self.model_name,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt},
            ],
            format='json',
            options=kwargs.get('options', {}),
        )
        return json.loads(response['message']['content'])
