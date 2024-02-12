from pydantic import TypeAdapter
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from exchange_rates.db.base import database
from exchange_rates.db.tables import Courses
from exchange_rates.logger import logger
from exchange_rates.models.domain import CoursesDTO


class CoursesRepository:
    async def get_all(
        self,
        exchanger: str | None = None,
        direction: str | None = None,
    ) -> list[CoursesDTO]:
        query = select(Courses)
        if exchanger:
            query = query.where(Courses.exchanger == exchanger)
        if direction:
            query = query.where(Courses.direction == direction)
        async with database.session() as session:
            courses = (await session.execute(query)).scalars().all()
        return TypeAdapter(list[CoursesDTO]).validate_python(courses)

    async def insert_course(
        self,
        exchanger: str,
        direction: str,
        value: float,
    ) -> None:
        query = insert(Courses).values(exchanger=exchanger, direction=direction, value=value)
        query = query.on_conflict_do_update(
            index_elements=[Courses.exchanger, Courses.direction],
            set_={
                "value": value,
            },
        )
        async with database.session() as session:
            await session.execute(query)
            logger.bind(exchanger=exchanger, direction=direction).debug("Updated course")
