from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "TripPlanner API"
    app_version: str = "0.1.0"
    api_v1_prefix: str = "/api/v1"

    database_url: str

    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    backend_reload: bool = False

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    frankfurter_base_url: str = "https://api.frankfurter.dev/v1"
    external_api_timeout_seconds: float = 5.0

    duffel_access_token: str = ""
    duffel_base_url: str = "https://api.duffel.com"
    duffel_api_version: str = "v2"

    supabase_url: str
    supabase_secret_key: str
    smtp_host: str = "smtp-relay.brevo.com"
    smtp_port: int = 2525
    smtp_username: str
    smtp_password: str
    smtp_from_email: str
    frontend_url: str
    email_verification_expire_hours: int = 24


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
