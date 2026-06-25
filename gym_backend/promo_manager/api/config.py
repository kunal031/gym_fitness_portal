from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Promo & Loyalty Manager"
    database_url: str = Field(
        default="postgresql+psycopg://admin:admin123@localhost:5432/promo_db",
        description="SQLAlchemy database URL for PostgreSQL."
    )
    create_tables_on_startup: bool = True
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

@lru_cache
def get_settings() -> Settings:
    return Settings()