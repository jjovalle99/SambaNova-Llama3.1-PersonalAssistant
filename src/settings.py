from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    samba_api_key: str
    samba_url: str
    news_api: str

    model_config = SettingsConfigDict(env_file=".env")
