from __future__ import annotations
from typing import TYPE_CHECKING
from dataclasses import dataclass

from src.core.service import BaseService, log_service_error

from src.apps.product.exceptions import (
    NotEnoughBalance,
    ProductDoesNotExist,
)

if TYPE_CHECKING:
    from src.apps.customer.models import Customer
    from src.apps.product.models import Product


@dataclass(kw_only=True, slots=True, frozen=True)
class BuyProductService(BaseService):
    @log_service_error
    def __call__(self, product_id: int, customer: Customer) -> dict:
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            raise ProductDoesNotExist(product_id=product_id, customer_id=customer.pk)

        if customer.balance < product.price:
            raise NotEnoughBalance(product_id=product_id, customer_id=customer.pk)

        # other business logic...
        return {"message": "Thank you for buying!"}
