from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, final

from apps.product.exceptions import NotEnoughBalance, ProductDoesNotExist, CustomerDoesNotExist
from apps.product.models import Product
from apps.core.service import log_service_error

if TYPE_CHECKING:
    from apps.customer.models import Customer


@final
@dataclass(kw_only=True, slots=True, frozen=True)
class BuyProductService:
    @log_service_error
    def __call__(self, *, product_id: int, customer: Customer) -> None:
        if not customer:
            raise CustomerDoesNotExist(
                product_id=product_id,
            )

        product = Product.objects.filter(pk=product_id).first()
        if product is None:
            raise ProductDoesNotExist(
                customer=dict(id=customer.pk),
                product=dict(id=product_id),
            )

        if customer.balance < product.price:
            raise NotEnoughBalance(
                customer=dict(id=customer.pk, balance=customer.balance),
                product=dict(id=product.pk, price=product.price, name=product.title),
            )

        customer.balance -= product.price
        customer.save(update_fields=["balance"])
