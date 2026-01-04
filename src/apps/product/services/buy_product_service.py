from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, final

from django.db import transaction

from apps.core.service import log_service_error
from apps.product.dtos import BuyProductIn, BuyProductOut
from apps.product.exceptions import (
    NotEnoughBalance,
    OutOfStockError,
    ProductNotAvailable,
    ProductNotFound,
)
from apps.product.models import Product

if TYPE_CHECKING:
    from apps.customer.models import Customer


@final
@dataclass(kw_only=True, slots=True, frozen=True)
class BuyProductService:
    product: BuyProductIn
    customer: Customer

    @log_service_error
    def __call__(self) -> BuyProductOut:
        product = Product.objects.filter(pk=self.product.id).first()
        if product is None:
            raise ProductNotFound(
                product=dict(id=self.product.id, count=self.product.count),
            )
        if product.count < self.product.count:
            raise OutOfStockError(
                product=dict(id=product.pk, count=product.count),
                order=dict(id=product.pk, count=self.product.count),
            )
        if not product.is_available:
            raise ProductNotAvailable(
                product=dict(id=self.product.id, count=self.product.count),
            )
        if not self._is_customer_can_buy_product(product=product):
            raise NotEnoughBalance(
                product=dict(id=self.product.id, count=self.product.count, price=product.price),
                customer=dict(id=self.customer.pk, balance=self.customer.balance),
            )
        return self._buy(product=product)

    def _is_customer_can_buy_product(self, *, product: Product) -> bool:
        total_price = product.calculate_total_price(self.product.count)
        return self.customer.balance > total_price

    @transaction.atomic
    def _buy(self, *, product: Product) -> BuyProductOut:
        self.customer.balance -= product.calculate_total_price(self.product.count)
        self.customer.save(update_fields=["balance"])
        product.count -= self.product.count
        product.save(update_fields=["count"])
        return BuyProductOut(
            product=self.product.id,
            count=self.product.count,
            balance=self.customer.balance,
        )
