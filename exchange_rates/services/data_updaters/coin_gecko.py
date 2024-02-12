import asyncio
from collections.abc import AsyncIterable, Iterable
from itertools import cycle
from typing import Any, ClassVar, cast

import httpx
from httpx import AsyncClient, HTTPError, HTTPStatusError
from yarl import URL

from exchange_rates.logger import logger
from exchange_rates.models.domain import CoursesDTO
from exchange_rates.resources import Directions, Exchangers

from .base import BaseDataUpdater


class CoinGeckoDataUpdater(BaseDataUpdater):
    _symbol_mapper: ClassVar[dict[tuple[str, str], Directions]] = {
        ("btcb", "usd"): Directions.BTC_USD,
        ("beth", "usd"): Directions.ETH_USD,
    }

    def __init__(self, ids: list[str], currencies: list[str], sleep: float, timeout: float = 1.0) -> None:
        self._ids = ids
        self._currencies = currencies
        self._base_url = URL("https://api.coingecko.com/api/v3/coins/markets")
        self._sleep = sleep
        self._retry_after = 0.0
        self._timeout = timeout

    def _url_for_currency(self, currency: str) -> URL:
        return self._base_url.with_query({"ids": ",".join(self._ids), "vs_currency": currency})

    def _set_retry_after(self, retry_after: float) -> None:
        self._retry_after = retry_after

    async def _smart_sleep(self) -> None:
        if not self._retry_after:
            await asyncio.sleep(self._sleep)
        else:
            logger.bind(duration=self._retry_after).debug("smart sleep")
            await asyncio.sleep(self._retry_after)
            self._set_retry_after(0)

    async def _make_request(self, currency: str) -> list[dict[str, Any]] | None:
        async with AsyncClient() as client:
            try:
                url = str(self._url_for_currency(currency.lower()))
                logger.bind(url=url).debug("request started")
                response = await client.get(url, timeout=self._timeout)
                logger.bind(url=url).debug("request finished")
                response.raise_for_status()
                return cast(list[dict[str, Any]], response.json())
            except HTTPStatusError as err:
                if err.response.status_code == httpx.codes.BAD_REQUEST:
                    logger.error(response.json()["error"])
                    return None
                if err.response.status_code == httpx.codes.TOO_MANY_REQUESTS:
                    logger.warning("Too many requests")
                    self._set_retry_after(float(err.response.headers.get("Retry-After", 0)))
                    return None
            except HTTPError as err:
                logger.bind(err=str(err)).warning("Not server error")
                return None
            return None

    def _parse_data(self, data: list[dict[str, Any]], currency: str) -> Iterable[CoursesDTO]:
        for course_obj in data:
            if direction := self._symbol_mapper.get((course_obj["symbol"], currency)):
                yield CoursesDTO(
                    exchanger=Exchangers.COIN_GECKO, direction=direction, value=course_obj["current_price"]
                )

    async def generate_messages(self) -> AsyncIterable[CoursesDTO]:
        for currency in cycle(self._currencies):
            data = await self._make_request(currency)
            if data is not None:
                for course in self._parse_data(data, currency):
                    logger.bind(**course.model_dump()).debug("Coingecko yield")
                    yield course
            await self._smart_sleep()
