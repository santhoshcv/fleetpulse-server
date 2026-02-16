"""Application configuration settings."""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings from environment variables."""

    # Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", "")

    # Server
    TCP_HOST: str = os.getenv("TCP_HOST", "0.0.0.0")
    TCP_PORT: int = int(os.getenv("TCP_PORT", "8888"))
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))

    # Application
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    MAX_CONNECTIONS: int = int(os.getenv("MAX_CONNECTIONS", "1000"))
    BUFFER_SIZE: int = int(os.getenv("BUFFER_SIZE", "4096"))

    # Database
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "20"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))

    @classmethod
    def validate(cls) -> bool:
        """Validate required settings are present."""
        required = [cls.SUPABASE_URL, cls.SUPABASE_KEY]
        return all(required)


settings = Settings()
