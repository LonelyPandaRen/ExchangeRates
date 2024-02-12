from enum import Enum
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_PATH = Path(__file__).parent.parent.parent.parent


class AppEnvTypes(str, Enum):
    PROD = "prod"
    DEV = "dev"
    TEST = "test"


class BaseAppSettings(BaseSettings):
    app_env: AppEnvTypes = AppEnvTypes.PROD
    model_config = SettingsConfigDict(env_file=(ROOT_PATH / ".env"), extra="ignore")
