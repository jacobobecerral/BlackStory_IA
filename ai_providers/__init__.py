from .base_provider import AIProvider
from .ollama_provider import OllamaProvider
from .gemini_provider import GeminiProvider
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider

def get_ai_provider(provider_name: str, model_name: str) -> AIProvider:
    if provider_name == "ollama":
        return OllamaProvider(model_name)
    elif provider_name == "gemini":
        return GeminiProvider(model_name)
    elif provider_name == "openai":
        return OpenAIProvider(model_name)
    elif provider_name == "anthropic":
        return AnthropicProvider(model_name)
    else:
        raise ValueError(f"Unknown AI provider: {provider_name}")
