from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    # Default (tanpa konfigurasi apa pun) : SQLite file lokal -> langsung jalan
    # Docker / PostgreSQL                 : postgresql+psycopg2://user:pass@host:5432/merit_polri
    DATABASE_URL: str = "sqlite:///./merit_polri.db"

    # Auto setup saat aplikasi start: tunggu database siap -> buat tabel -> isi data awal (jika masih kosong)
    AUTO_SETUP: bool = True
    DB_CONNECT_RETRIES: int = 30
    DB_CONNECT_DELAY: float = 2.0

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
