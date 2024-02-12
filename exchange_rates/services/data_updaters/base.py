from abc import ABC, abstractmethod
from collections.abc import AsyncIterable

from exchange_rates.logger import logger
from exchange_rates.models.domain import CoursesDTO
from exchange_rates.task_iq.tasks import set_course


class BaseDataUpdater(ABC):
    @abstractmethod
    async def generate_messages(self) -> AsyncIterable[CoursesDTO]:
        # https://mypy.readthedocs.io/en/stable/more_types.html#typing-async-await
        raise NotImplementedError
        if False:
            yield 0

    async def publish_messages(self) -> None:
        async for message in self.generate_messages():
            logger.bind(**message.model_dump()).debug("Message published")
            await set_course.kiq(**message.model_dump())
