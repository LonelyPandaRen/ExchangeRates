from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Depends
from fastapi_cache.decorator import cache
from pydantic.json_schema import SkipJsonSchema

from exchange_rates.db.repositories.courses import CoursesRepository
from exchange_rates.models.schemas.courses import CoursesSchema
from exchange_rates.resources import Directions, Exchangers

if TYPE_CHECKING:  # pragma: no cover
    from exchange_rates.models.domain import CoursesDTO

courses_router = APIRouter(prefix="/courses")


@courses_router.get(
    path="/",
    response_model=list[CoursesSchema],
)
@cache(expire=1)
async def get_courses(
    courses_repository: Annotated[CoursesRepository, Depends()],
    direction: Directions | SkipJsonSchema[None] = None,
    exchanger: Exchangers | SkipJsonSchema[None] = None,
) -> list["CoursesDTO"]:
    return await courses_repository.get_all(
        direction=direction,
        exchanger=exchanger,
    )
