from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional



class Settings(BaseSettings):
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str
    DATA_GOV_IN_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None


    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()