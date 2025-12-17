from core.service import BaseServiceError


class NotEnoughBalance(BaseServiceError):
    """Not enough balance"""


class ProductDoesNotExist(BaseServiceError):
    """Product not found"""
