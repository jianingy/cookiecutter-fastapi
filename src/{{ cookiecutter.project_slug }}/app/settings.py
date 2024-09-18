from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=os.environ.get('ERATO_ENV_FILE', '.env'), env_file_encoding='utf-8')

    debug: bool = Field(default=False)

    database_url: PostgresDsn = Field(default=...)
    database_max_connections: int = Field(default=10)
    echo_sql: bool = Field(default=False)

    admin_token_secret_key: str = Field(default='admin_token')
    admin_token_algorithm: str = Field(default='HS256')
    admin_token_expire_seconds: int = Field(default=3600)

    celery_broker_url: RedisDsn = Field(default=...)
    celery_backend_url: RedisDsn = Field(default=...)


settings = Settings()
