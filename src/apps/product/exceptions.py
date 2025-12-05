from src.core import BaseServiceException


class NotEnoughBalance(BaseServiceException):
    """User has not enough money on his balance"""


class ProductDoesNotExist(BaseServiceException):
    """Product does not exist"""
