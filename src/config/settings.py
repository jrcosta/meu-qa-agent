import os
from dataclasses import dataclass
from dotenv import load_dotenv
from typing import Any

# carrega variáveis do arquivo .env
load_dotenv()


@dataclass
class Settings:
    llm_provider: str = os.getenv("LLM_PROVIDER", "groq")

    llm_model: str = os.getenv(
        "LLM_MODEL",
        "groq/llama-3.3-70b-versatile"
    )

    llm_api_key: str = os.getenv(
        "LLM_API_KEY",
        ""
    )

    llm_base_url: str = os.getenv(
        "LLM_BASE_URL",
        "https://api.groq.com/openai/v1"
    )

    llm_temperature: float = float(
        os.getenv("LLM_TEMPERATURE", "0.2")
    )

    # Provide a method to build an LLM client from this settings instance.
    # QAAgentFactory._resolve_llm looks for methods like 'create_llm' on the
    # settings object, so exposing this keeps backwards compatibility.
    def create_llm(self):
        """
        Return a value compatible with the `crewai.Agent` `llm` parameter.

        The `Agent` model accepts either a string model identifier or an
        instance of the framework's BaseLLM. Returning the configured
        model string is the safest, dependency-free option for CI runs.
        """

        # Prefer returning the model identifier (string). If in the future
        # you want to return a richer object (e.g. an LLM client), ensure it
        # implements the interface expected by `crewai.Agent`.
        return self.llm_model


def get_settings() -> Settings:
    return Settings()


def create_llm_from_settings(settings: Settings):
    """
    Helper factory to build an LLM client from a Settings instance.

    This function performs the import locally to avoid circular imports
    between settings and the LLM client implementation.
    """
    from src.services.llm_client import LLMClient

    return LLMClient(settings)


# Backwards-compatible method name expected by QAAgentFactory/_resolve_llm
def create_llm() -> Any:
    """Create an LLM value using the default settings.

    Delegates to the `Settings.create_llm()` instance method to produce a
    value compatible with `QAAgentFactory._resolve_llm()` and the `Agent`
    constructor.
    """
    settings = get_settings()
    return settings.create_llm()