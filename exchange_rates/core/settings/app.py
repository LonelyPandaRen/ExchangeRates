from functools import cached_property
from typing import Any, ClassVar, Literal, TypeAlias

from pydantic import AmqpDsn, Field, PostgresDsn, RedisDsn, ValidationInfo, field_validator
from pydantic_settings import SettingsConfigDict
from yarl import URL

from exchange_rates.core.settings.base import BaseAppSettings

VpnPoolType: TypeAlias = dict[str, dict[str, str]]


def build_db_url(data: dict[str, Any], db_prefix: str = "") -> URL:
    return URL.build(
        scheme="postgresql+asyncpg",
        user=data["postgres_user"],
        password=data["postgres_password"],
        host=data["postgres_host"],
        path=f"/{db_prefix}{data['postgres_db'] or ''}",
        port=data["postgres_port"],
    )


class AppSettings(BaseAppSettings):
    # app
    debug: bool = False

    root_path: str = ""
    docs_url: str = "/docs"
    openapi_url: str = "/openapi.json"
    redoc_url: str = "/redoc"

    title: str = "Exchange Rates"
    version: str = "0.1.0"

    # db
    postgres_host: str
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_port: int = 5432
    postgres_db_prefix: ClassVar[str] = ""
    database_uri: PostgresDsn | None = None

    # hosting
    allowed_hosts: list[str] = ["*"]
    internal_port: int = Field(default=8080, gt=0, lt=2**16)
    internal_host: str = "localhost"

    # broker
    rmq_host: str = "localhost"
    rmq_vhost: str = "/"
    rmq_pass: str = "guest"
    rmq_user: str = "guest"
    rmq_port: int = 5672
    broker_uri: AmqpDsn | None = None
    use_in_memory_broker: bool = False

    # redis
    redis_url: RedisDsn

    # logging
    log_level: Literal["TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    use_json_logs: bool = True

    model_config = SettingsConfigDict(validate_assignment=True, env_nested_delimiter="__")

    @field_validator("database_uri", mode="before")
    def assemble_db_connection(cls, v: str | None, info: ValidationInfo) -> PostgresDsn:
        if isinstance(v, str):
            return PostgresDsn(v)
        return PostgresDsn(str(build_db_url(info.data, cls.postgres_db_prefix)))

    @field_validator("broker_uri", mode="before")
    def assemble_broker_connection(cls, v: str | None, info: ValidationInfo) -> AmqpDsn:
        if isinstance(v, str):
            return AmqpDsn(v)
        return AmqpDsn(
            str(
                URL.build(
                    scheme="amqp",
                    user=info.data["rmq_user"],
                    password=info.data["rmq_pass"],
                    host=info.data["rmq_host"],
                    path=info.data["rmq_vhost"],
                    port=info.data["rmq_port"],
                ),
            ),
        )

    @cached_property
    def fastapi_kwargs(self) -> dict[str, Any]:
        return {
            "debug": self.debug,
            "root_path": self.root_path,
            "docs_url": self.docs_url,
            "openapi_url": self.openapi_url,
            "redoc_url": self.redoc_url,
            "title": self.title,
            "version": self.version,
        }
