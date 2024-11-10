from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    samba_api_key: str
    samba_url: str
    credentials_path: Path = "credentials.json"
    gmail_host_user: str
    timezone: str = "Europe/London"

    model_config = SettingsConfigDict(env_file=".env")
