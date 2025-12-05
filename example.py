from dataclasses import dataclass
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


class FirstLessThanSecond(BaseServiceException):
    """First must be grater than second"""


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


@dataclass(kw_only=True, slots=True, frozen=True)
class FirstSecondService(BaseService):
    @log_service_error
    def __call__(self, first: int, second: int) -> dict:
        if first < second:
            raise FirstLessThanSecond(first=first, second=second)

        # other business logic...
        return {"message": "Thank you for buying!"}


class Controller:
    def process(self) -> dict:
        # some validation before
        try:
            FirstSecondService()(first=1, second=2)
        except FirstLessThanSecond as exc:
            return {"error": exc.message}

        return {"message": "Ok"}


result = Controller().process()
print(result)
