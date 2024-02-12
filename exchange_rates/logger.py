import sys
from typing import TYPE_CHECKING

from loguru import logger as loguru_logger

from exchange_rates.core.config import settings

if TYPE_CHECKING:  # pragma: no cover
    from loguru import Logger


def _get_logger() -> "Logger":
    if not settings.use_json_logs:
        loguru_logger.remove()  # удаляем дефолтные обработчики чтобы не спамить лишнего
        loguru_logger.add(sys.stderr, level=settings.log_level, format="[{time:HH:mm:ss}] {message} (context: {extra})")
        return loguru_logger

    _logger: "Logger" = loguru_logger.bind(name="json_logger")
    _logger.remove()  # удаляем дефолтные обработчики чтобы не спамить лишнего
    _logger.add(sys.stdout, format="{message}", serialize=settings.use_json_logs, level=settings.log_level)
    return _logger


logger = _get_logger()
