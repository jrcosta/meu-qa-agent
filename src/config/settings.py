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
        from src.services.llm_client import LLMClient

        return LLMClient(self)


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
    """Create an LLM client using the default settings.

    This function exists so callers that call `settings.create_llm()` can
    still work when `get_settings()` returns a plain `Settings` dataclass.
    It will build the client using the default settings returned by
    `get_settings()`.
    """
    settings = get_settings()
    return create_llm_from_settings(settings)