from apps.core.service import BaseServiceError


class NotEnoughBalance(BaseServiceError):
    """Not enough balance"""


class ProductNotFound(BaseServiceError):
    """Product not found"""


class ProductNotAvailable(BaseServiceError):
    """Product not available now"""


class OutOfStockError(BaseServiceError):
    """Product is out of stock"""
