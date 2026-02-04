from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://app:app@localhost:5432/app"
    storage_root: str = "./storage"
    cors_origins: str = "http://localhost:5173"

    # Ops module
    ops_warn_threshold: int = 80  # percent used
    ops_trash_retention_days: int = 30

    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
