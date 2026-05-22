import json
import logging
import sys
from contextvars import ContextVar
from datetime import datetime
from typing import Any

from app.core.config import settings

request_id_context: ContextVar[str | None] = ContextVar(
    'request_id',
    default=None,
)


class JsonLogFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'environment': settings.app_env,
        }

        request_id = request_id_context.get()
        if request_id:
            payload['request_id'] = request_id

        if record.exc_info:
            payload['exception'] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)


class TextLogFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        request_id = request_id_context.get() or '-'
        return (
            f'{datetime.utcnow().isoformat()} '
            f'[{record.levelname}] '
            f'[{record.name}] '
            f'[request_id={request_id}] '
            f'{record.getMessage()}'
        )


def setup_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonLogFormatter())

    log_level = getattr(settings, 'log_level', 'INFO')

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level.upper())

    logging.getLogger('uvicorn.access').handlers.clear()


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
