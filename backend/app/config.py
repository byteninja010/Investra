"""
Application configuration — loads environment variables and creates the shared LLM instance.
The LLM is configured via base_url + model so you can swap providers
(OpenAI, Groq, Together, etc.) without touching any code.
"""


from pydantic_settings import BaseSettings
from functools import lru_cache
from langchain_openai import ChatOpenAI


class Settings(BaseSettings):
    # LLM
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_BASE_URL: str = "https://api.openai.com/v1"
    LLM_API_KEY: str = ""

    # Tavily
    TAVILY_API_KEY: str = ""

    # LangSmith
    LANGSMITH_TRACING: bool = False
    LANGSMITH_API_KEY: str = ""
    LANGSMITH_PROJECT: str = "finance-research-agents"

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()


def get_llm(temperature: float = 0.1) -> ChatOpenAI:
    """Return a ChatOpenAI instance that can target any OpenAI-compatible API."""
    settings = get_settings()
    return ChatOpenAI(
        model=settings.LLM_MODEL,
        base_url=settings.LLM_BASE_URL,
        api_key=settings.LLM_API_KEY,
        temperature=temperature,
        max_retries=6,
        timeout=60,
    )

