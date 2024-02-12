from exchange_rates.core.settings.app import AppSettings


class DevAppSettings(AppSettings):
    debug: bool = True
    title: str = "Dev Exchange Rates"
    use_in_memory_broker: bool = True
