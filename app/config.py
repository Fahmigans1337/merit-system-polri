from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    # Production (Docker): postgresql+psycopg2://postgres:postgres@db:5432/merit_polri
    # Local dev (SQLite) : sqlite:///./merit_polri.db
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@db:5432/merit_polri"

    # JWT
    SECRET_KEY: str = "merit-system-polri-secret-key-2026-CHANGE-IN-PRODUCTION"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # App
    APP_NAME: str = "Merit System Personel Polri"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
