# new congig.py

from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Billing Manager"
    # Notice this connects specifically to billing_db, NOT membership_db
    database_url: str = Field(
        default="postgresql+psycopg://admin:admin123@localhost:5432/billing_db",
        description="SQLAlchemy database URL for PostgreSQL."
    )
    # The URL where Service A is running so we can verify plans
    service_a_url: str = Field(default="http://localhost:8000")
    service_c_url: str = Field(default="http://localhost:8002")
    service_d_url: str = Field(default="http://localhost:8003")
    
    create_tables_on_startup: bool = True
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

@lru_cache
def get_settings() -> Settings:
    return Settings()