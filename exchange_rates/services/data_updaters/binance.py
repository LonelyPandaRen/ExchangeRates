import asyncio
import json
from collections.abc import AsyncIterable
from typing import ClassVar

from websockets import ConnectionClosed, connect
from yarl import URL

from exchange_rates.logger import logger
from exchange_rates.models.domain import CoursesDTO
from exchange_rates.resources import Directions, Exchangers

from .base import BaseDataUpdater


class BinanceDataUpdater(BaseDataUpdater):
    _symbol_mapper: ClassVar[dict[str, Directions]] = {
        "BTCUSDT": Directions.BTC_USD,
        "ETHUSDT": Directions.ETH_USD,
    }

    def __init__(self, streams: list[str], sleep: float) -> None:
        self._base_url = URL("wss://stream.binance.com:9443/stream")
        self._streams = streams
        self._sleep = sleep

    @property
    def _ulr(self) -> URL:
        return self._base_url.with_query({"streams": "/".join(self._streams)})

    def _parse_msg(self, msg: str | bytes) -> CoursesDTO | None:
        msg_data = json.loads(msg)["data"]
        direction = self._symbol_mapper.get(msg_data["s"])
        if direction is None:
            # not supported
            return None
        return CoursesDTO(
            exchanger=Exchangers.BINANCE,
            direction=direction,
            value=float(msg_data["p"]),
        )

    async def generate_messages(self) -> AsyncIterable[CoursesDTO]:
        while True:
            try:
                async with connect(str(self._ulr), ping_interval=60, ping_timeout=180) as websocket:
                    async for msg in websocket:
                        if course := self._parse_msg(msg):
                            logger.bind(**course.model_dump()).debug("Binance yield")
                            yield course
                        await asyncio.sleep(self._sleep)
            except ConnectionClosed:
                logger.error("Reconnecting to binance websocket")
