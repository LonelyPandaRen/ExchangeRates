from taskiq import AsyncBroker, InMemoryBroker
from taskiq_aio_pika import AioPikaBroker

from exchange_rates.core.config import settings

async_broker: AsyncBroker = AioPikaBroker(url=str(settings.broker_uri))

if settings.use_in_memory_broker:
    async_broker = InMemoryBroker()
