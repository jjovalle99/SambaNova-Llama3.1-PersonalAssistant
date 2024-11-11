from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str
    samba_api_key: str
    samba_url: str
    credentials_path: Path = "credentials.json"
    gmail_host_user: str
    timezone: str = "Europe/London"
    weatherstack_api_key: str
    worlds_news_api_key: str

    model_config = SettingsConfigDict(env_file=".env")
