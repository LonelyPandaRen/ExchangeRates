from asyncio import current_task
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from pydantic.alias_generators import to_snake
from sqlalchemy.ext.asyncio import async_scoped_session, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, declared_attr

from exchange_rates.core.config import settings

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import AsyncIterator

    from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession


class Base(DeclarativeBase):
    @classmethod
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return to_snake(cls.__name__)

    def __repr__(self) -> str:
        return str(self)


class Database:
    def __init__(self) -> None:
        self.engine: AsyncEngine = create_async_engine(
            str(settings.database_uri),
            pool_pre_ping=True,
            pool_size=20,
        )
        self.async_session_factory = async_scoped_session(
            async_sessionmaker(
                autocommit=False,
                expire_on_commit=False,
                autoflush=False,
                bind=self.engine,
            ),
            scopefunc=current_task,
        )

    @asynccontextmanager
    async def session(self) -> "AsyncIterator[AsyncSession]":
        session: AsyncSession = self.async_session_factory()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            session.expire_all()
            raise
        finally:
            await session.close()


database = Database()
