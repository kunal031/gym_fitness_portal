# new config.py
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Attendance Manager"
    # Pointing securely to the dedicated attendance database
    database_url: str = Field(
        default="postgresql+psycopg://admin:admin123@localhost:5432/attendance_db",
        description="SQLAlchemy database URL for PostgreSQL."
    )
    service_a_url: str = Field(default="http://localhost:8000")
    create_tables_on_startup: bool = True

    internal_api_key: str = Field(default="super-secret-gym-key-123")
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

@lru_cache
def get_settings() -> Settings:
    return Settings()