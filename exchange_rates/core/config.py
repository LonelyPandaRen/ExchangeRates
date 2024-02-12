from functools import cache
from typing import TYPE_CHECKING

from exchange_rates.core.settings.base import AppEnvTypes, BaseAppSettings
from exchange_rates.core.settings.development import DevAppSettings
from exchange_rates.core.settings.production import ProdAppSettings
from exchange_rates.core.settings.test import TestAppSettings

if TYPE_CHECKING:  # pragma: no cover
    from exchange_rates.core.settings.app import AppSettings

environments: dict[AppEnvTypes, type["AppSettings"]] = {
    AppEnvTypes.DEV: DevAppSettings,
    AppEnvTypes.PROD: ProdAppSettings,
    AppEnvTypes.TEST: TestAppSettings,
}


@cache
def get_app_settings() -> "AppSettings":
    """Можно использовать в Depends."""
    app_env = BaseAppSettings().app_env
    config = environments[app_env]
    return config()


settings = get_app_settings()
