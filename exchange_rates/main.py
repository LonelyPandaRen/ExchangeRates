from collections.abc import Callable

import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

from exchange_rates.api.routers.base import base_router
from exchange_rates.core.config import settings


# TODO: mypy
def _request_key_builder(  # type: ignore[no-untyped-def]
    func: Callable,  # type: ignore[type-arg] # noqa: ARG001
    namespace: str = "",
    *,
    request: Request,
    response: Response,  # noqa: ARG001
    **kwargs,  # noqa: ARG001
) -> str:
    return ":".join(
        [
            namespace,
            request.method.lower(),
            request.url.path,
            repr(sorted(request.query_params.items())),
        ]
    )


async def startup() -> None:
    redis = aioredis.from_url(str(settings.redis_url))
    FastAPICache.init(
        RedisBackend(redis),
        prefix="fastapi-cache",
        key_builder=_request_key_builder,
    )


def get_application() -> FastAPI:
    application = FastAPI(
        **settings.fastapi_kwargs,
        swagger_ui_parameters={
            "displayOperationId": True,
        },
    )

    application.include_router(base_router)
    application.add_event_handler("startup", startup)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_hosts,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return application


app = get_application()

if __name__ == "__main__":
    uvicorn.run(app, host=settings.internal_host, port=settings.internal_port, loop="asyncio")
