from exchange_rates.db.repositories.courses import CoursesRepository

from .broker import async_broker


@async_broker.task()
async def set_course(
    exchanger: str,
    direction: str,
    value: float,
) -> None:
    await CoursesRepository().insert_course(
        exchanger=exchanger,
        direction=direction,
        value=value,
    )
