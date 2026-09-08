from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Membership Manager"
    # Format: postgresql+psycopg://username:password@localhost:5432/database_name
    database_url: str = Field(
        default="postgresql+psycopg://admin:admin123@localhost:5432/membership_db",
        description="SQLAlchemy database URL for PostgreSQL.",
    )
    create_tables_on_startup: bool = True

    # --- New Auth Settings ---
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
