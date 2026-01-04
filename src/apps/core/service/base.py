import logging
from functools import wraps
from typing import Any, Callable, Protocol

logger = logging.LoggerAdapter(
    logging.getLogger(__name__), extra={"tag": "service-layer"}
)


class IService(Protocol):
    def __call__(self, **kwargs) -> Any:
        """Business logic here. Use only keyword arguments."""


class BaseServiceError(Exception):
    def __init__(self, message: str = None, **context) -> None:
        self.message = message or self.__doc__
        self.context = context


def log_service_error(__call__: Callable) -> Callable:
    @wraps(__call__)
    def wrapper(self, **kwargs) -> Any:
        try:
            return __call__(self, **kwargs)
        except BaseServiceError as error:
            logger.error(
                {
                    "error_in": self.__class__.__name__,
                    "error_name": error.__class__.__name__,
                    "error_message": error.message,
                    "error_context": dict(**error.context),
                },
            )
            raise error

    return wrapper
