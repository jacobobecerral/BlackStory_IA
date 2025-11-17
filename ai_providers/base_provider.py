from abc import ABC, abstractmethod
from typing import Dict, Any

class AIProvider(ABC):
    def __init__(self, model_name: str):
        self.model_name = model_name

    @abstractmethod
    async def generate_text(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        """
        Generates text based on the given system and user prompts.
        """
        pass

    @abstractmethod
    async def generate_json(self, system_prompt: str, user_prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Generates JSON output based on the given system and user prompts.
        """
        pass
