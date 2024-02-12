from typing import ClassVar

from exchange_rates.core.settings.app import AppSettings


class TestAppSettings(AppSettings):
    debug: bool = True
    title: str = "Test Exchange Rates"
    postgres_db_prefix: ClassVar[str] = "test_"
    use_in_memory_broker: bool = True
