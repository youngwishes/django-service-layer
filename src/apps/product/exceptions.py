from apps.core.service import BaseServiceError


class NotEnoughBalance(BaseServiceError):
    """Not enough balance"""


class ProductDoesNotExist(BaseServiceError):
    """Product not found"""

class CustomerDoesNotExist(BaseServiceError):
    """Please make sure that you created customer"""