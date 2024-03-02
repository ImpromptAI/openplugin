from enum import Enum
from typing import Any, Optional

from pydantic import BaseConfig, BaseModel


class Config(BaseModel):
    """
    Represents the API configuration for a plugin.
    """

    provider: str = "openai"
    openai_api_key: Optional[str] = None
    cohere_api_key: Optional[str] = None
    google_palm_key: Optional[str] = None
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region_name: Optional[str] = None
    azure_api_key: Optional[str] = None


class LLM(BaseModel):
    """
    Represents the configuration for an LLM (Language Model) provider.
    """

    provider: str
    model_name: str
    temperature: float = 0
    max_tokens: int = 2048
    top_p: float = 1
    frequency_penalty: float = 0
    presence_penalty: float = 0
    n: int = 1
    best_of: int = 1
    max_retries: int = 6

    class Config(BaseConfig):
        # Set protected_namespaces to an empty tuple to resolve the conflict
        protected_namespaces = ()
