"""
Central app configuration. All secrets/config come from environment variables
(.env locally, real env vars in Render/production). Never hardcode secrets.
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    ENV: str = "development"

    JWT_SECRET: str = "dev-only-insecure-secret-change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    MONGO_URI: str = ""
    MONGO_DB_NAME: str = "beejbazaar"

    FIREBASE_PROJECT_ID: str = ""
    FIREBASE_CREDENTIALS_JSON: str = ""

    CLOUDINARY_URL: str = ""
    GEMINI_API_KEY: str = ""

    ALLOWED_ORIGINS: str = "http://localhost:5173"

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    @property
    def USE_MOCK_DB(self) -> bool:
        return not self.MONGO_URI

    @property
    def USE_MOCK_FIREBASE(self) -> bool:
        return not self.FIREBASE_PROJECT_ID or not self.FIREBASE_CREDENTIALS_JSON

    class Config:
        env_file = ".env"


settings = Settings()
