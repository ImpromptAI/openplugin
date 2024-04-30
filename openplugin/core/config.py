import os
from typing import Optional

from pydantic import BaseModel


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

    def replace_missing_with_system_keys(self):
        if not self.openai_api_key and os.environ.get("OPENAI_API_KEY"):
            self.openai_api_key = os.environ["OPENAI_API_KEY"]
