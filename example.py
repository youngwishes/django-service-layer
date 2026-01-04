import logging
from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable, Protocol, final

logger = logging.LoggerAdapter(
    logging.getLogger(__name__), extra={"tag": "service-layer"}
)


class BaseService(Protocol):
    def __call__(self, **kwargs) -> Any:
        """Business logic here. Use only keyword arguments."""


class BaseServiceException(Exception):
    def __init__(self, message: str = None, **context) -> None:
        self.message = message or self.__doc__
        self.context = context


class NotEnoughBalance(BaseServiceException):
    """Not enough balance"""


def log_service_error(__call__: Callable) -> Callable:
    @wraps(__call__)
    def wrapper(self, **kwargs) -> Any:
        try:
            return __call__(self, **kwargs)
        except BaseServiceException as error:
            logger.error(
                {
                    "error_in": self.__class__.__name__,
                    "error_name": error.__class__.__name__,
                    "error_message": error.message,
                    **error.context,
                }
            )
            raise error

    return wrapper


@final
@dataclass(kw_only=True, slots=True, frozen=True)
class BuyProductService:
    balance: float
    price: float

    @log_service_error
    def __call__(self) -> None:
        if self.balance < self.price:
            raise NotEnoughBalance(price=self.price, balance=self.balance)
        # ...any other business logic & checks...
