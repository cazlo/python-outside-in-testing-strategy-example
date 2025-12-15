import os
from pydantic_core.core_schema import FieldValidationInfo
from pydantic import PostgresDsn, AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Any
from enum import Enum


class ModeEnum(str, Enum):
    development = "development"
    production = "production"
    testing = "testing"


class Settings(BaseSettings):
    MODE: ModeEnum = ModeEnum.development
    API_VERSION: str = "v1"
    API_V1_STR: str = f"/api/{API_VERSION}"
    PROJECT_NAME: str

    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"
    RABBITMQ_HOST: str = "rabbitmq"
    RABBITMQ_PORT: int = 5672


    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_HOST: str
    DATABASE_PORT: int
    DATABASE_NAME: str
    DATABASE_CELERY_NAME: str = "celery_schedule_jobs"
    DB_POOL_SIZE: int = 83
    WEB_CONCURRENCY: int = 9
    POOL_SIZE: int = max(DB_POOL_SIZE // WEB_CONCURRENCY, 5)
    ASYNC_DATABASE_URI: PostgresDsn | str = ""

    @field_validator("ASYNC_DATABASE_URI", mode="after")
    def assemble_db_connection(cls, v: str | None, info: FieldValidationInfo) -> Any:
        if isinstance(v, str):
            if v == "":
                return PostgresDsn.build(
                    scheme="postgresql+asyncpg",
                    username=info.data["DATABASE_USER"],
                    password=info.data["DATABASE_PASSWORD"],
                    host=info.data["DATABASE_HOST"],
                    port=info.data["DATABASE_PORT"],
                    path=info.data["DATABASE_NAME"],
                )
        return v

    SYNC_CELERY_DATABASE_URI: PostgresDsn | str = ""

    @field_validator("SYNC_CELERY_DATABASE_URI", mode="after")
    def assemble_celery_db_connection(
        cls, v: str | None, info: FieldValidationInfo
    ) -> Any:
        if isinstance(v, str):
            if v == "":
                # celery uses non-standard connetion string which can no longer be built with PostgresDsn
                return f"db+postgresql://{info.data['DATABASE_USER']}:{info.data['DATABASE_PASSWORD']}@{info.data['DATABASE_HOST']}:{info.data['DATABASE_PORT']}/{info.data['DATABASE_CELERY_NAME']}?sslmode=disable"
                # return PostgresDsn.build(
                #     scheme="db+postgresql",
                #     username=info.data["DATABASE_USER"],
                #     password=info.data["DATABASE_PASSWORD"],
                #     host=info.data["DATABASE_HOST"],
                #     port=info.data["DATABASE_PORT"],
                #     path=info.data["DATABASE_CELERY_NAME"],
                # )
        return v

    BACKEND_CORS_ORIGINS: list[str] | list[AnyHttpUrl]

    @field_validator("BACKEND_CORS_ORIGINS")
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    model_config = SettingsConfigDict(
        case_sensitive=True, 
        env_file=[
            os.path.join(os.path.dirname(__file__), "../../../.env"),       # Default config (loaded first)
            os.path.join(os.path.dirname(__file__), "../../../.env.test"),  # Test overrides (takes precedence)
        ],
        env_file_encoding='utf-8',
        extra='ignore'  # Allow extra fields from .env that aren't defined in Settings
    )


settings = Settings()
