import os
from typing import Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    app_name: str = "Openplugin"
    azure_api_key: Optional[str] = os.environ.get("AZURE_API_KEY")


settings = Settings()
