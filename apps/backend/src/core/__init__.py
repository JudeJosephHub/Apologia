"""Apologia backend core configuration."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    app_name: str = "Apologia"
    debug: bool = False
    backend_secret_key: str = "change-me"
    backend_cors_origins: str = "http://localhost:3000,http://localhost:3001"

    # Supabase
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    database_url: str = ""

    # AI – OpenAI / Groq / AssemblyAI (from Sermonopedia)
    openai_api_key: str = ""
    groq_api_key: str = ""
    assemblyai_api_key: str = ""

    # AI – AWS Bedrock (from Apologia)
    aws_region: str = "us-east-1"
    bedrock_agent_id: str = ""
    bedrock_agent_alias_id: str = ""

    # AI – Grok / xAI (from Apologia)
    grok_api_key: str = ""
    grok_api_url: str = "https://api.x.ai/v1/chat/completions"
    grok_model: str = "grok-4-latest"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # SermonAudio
    sermonaudio_api_key: str = ""

    # Storage paths (from Apologia)
    upload_dir: str = "uploads"
    storage_dir: str = "storage"

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.backend_cors_origins.split(",") if o.strip()]

    @property
    def upload_path(self) -> Path:
        p = Path(self.upload_dir)
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def storage_path(self) -> Path:
        p = Path(self.storage_dir)
        p.mkdir(parents=True, exist_ok=True)
        return p


@lru_cache
def get_settings() -> Settings:
    return Settings()
