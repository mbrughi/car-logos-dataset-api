from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyUrl
from typing import List

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "Car Logos API"
    APP_ENV: str = "dev"
    APP_DEBUG: bool = True
    APP_HOST: str = "127.0.0.1"
    APP_PORT: int = 8000

    DB_USER: str = "carlogos"
    DB_PASS: str = "supersecret"
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_NAME: str = "carlogos"
    DATABASE_URL: str | None = None

    CORS_ORIGINS: str = ""

    STORAGE_ROOT: str = "/home/carlogosapi-api/htdocs/api.carlogosapi.com"
    PUBLIC_BASE_URL: str = "http://127.0.0.1:8000"

    API_KEYS_ENABLED: bool = True
    API_KEY_HEADER: str = "X-Api-Key"
    ADMIN_API_KEYS: str = ""

    REDIS_URL: str | None = "redis://127.0.0.1:6379/0"
    RL_WINDOW_SECONDS: int = 600
    RL_MAX_REQUESTS: int = 600
    REQLOG_TTL_SECONDS: int = 60*60*24*30
    REQLOG_MAX_ITEMS: int = 1000


    @property
    def sqlalchemy_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASS}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def cors_origins(self) -> List[str]:
        if not self.CORS_ORIGINS:
            return []
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

settings = Settings()
