from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "VisaSponsor API"
    environment: str = "development"
    api_prefix: str = "/api/v1"
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/visasponsor"
    sync_database_url: str = "postgresql://postgres:postgres@localhost:5432/visasponsor"
    redis_url: str | None = "redis://localhost:6379/0"
    enable_cache: bool = True
    cache_ttl_seconds: int = 300

    cors_origins: list[str] = ["http://localhost:3000"]
    requests_per_minute: int = 120

    clerk_jwks_url: str = "https://clerk.example.com/.well-known/jwks.json"
    clerk_issuer: str = "https://clerk.example.com"
    clerk_audience: str | None = None
    allow_dev_auth_bypass: bool = False
    dev_auth_user_id: str = "dev-user"
    dev_auth_email: str = "dev@example.com"

    dol_dataset_base_url: str = "https://www.dol.gov/sites/dolgov/files/ETA/oflc/pdfs"
    admin_ingestion_token: str = "change-me"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
