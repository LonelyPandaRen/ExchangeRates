from fastapi import APIRouter

from .courses import courses_router

base_router = APIRouter(prefix="/api")

v1_router = APIRouter(prefix="/v1")

v1_router.include_router(courses_router, tags=["courses"])

base_router.include_router(v1_router)
