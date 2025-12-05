from functools import wraps
from typing import Any, Callable
import abc
import logging

logger = logging.LoggerAdapter(logging.getLogger(__name__), extra={"tag": "service-layer"})


class BaseService(abc.ABC):
    @abc.abstractmethod
    def __call__(self, *args, **kwargs) -> Any:
        """Business logic here"""


class BaseServiceException(Exception):
    def __init__(self, message: str = None, service: str = None, **kwargs) -> None:
        self.message = message or self.__doc__
        self.service = service or self.__class__.__name__
        self.kwargs = kwargs


def log_service_error(service: Callable) -> Callable:
    @wraps(service)
    def wrapper(self, *args, **kwargs) -> Any:
        try:
            return service(self, *args, **kwargs)
        except BaseServiceException as exc:
            logger.error(
                {
                    "service": exc.service,
                    "message": exc.message,
                    **exc.kwargs,
                }
            )
            raise exc
    return wrapper
