"""
Настройки приложения, читаются из переменных окружения (.env).

Pydantic Settings сам подхватит .env файл и провалидирует,
что все обязательные переменные заданы — если что-то забыли,
приложение не запустится с понятной ошибкой, а не упадёт
где-то в середине работы.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    debug: bool = False
    database_url: str = "sqlite:///./notes_dev.db"
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60


settings = Settings()
