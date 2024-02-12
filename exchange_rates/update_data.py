import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from exchange_rates.services.data_updaters.binance import BinanceDataUpdater
from exchange_rates.services.data_updaters.coin_gecko import CoinGeckoDataUpdater
from exchange_rates.task_iq.broker import async_broker

binance_updater = BinanceDataUpdater(
    streams=[
        "btcusdt@aggTrade",
        "ethusdt@aggTrade",
    ],
    sleep=0.2,
)

coingecko_updater = CoinGeckoDataUpdater(
    ids=[
        "binance-bitcoin",
        "binance-eth",
    ],
    currencies=[
        "rub",
        "usd",
    ],
    sleep=5.0,
)


@asynccontextmanager
async def setup_broker() -> AsyncIterator[None]:
    await async_broker.startup()
    yield
    await async_broker.shutdown()


async def run_updates() -> None:
    async with setup_broker():
        await asyncio.gather(
            binance_updater.publish_messages(),
            coingecko_updater.publish_messages(),
        )


if __name__ == "__main__":
    asyncio.run(run_updates())
