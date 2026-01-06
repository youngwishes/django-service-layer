from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, final

from django.db import transaction

from apps.core.service import log_service_error
from apps.product.exceptions import (
    NotEnoughBalance,
    OutOfStockError,
    ProductNotAvailable,
    ProductNotFound,
)
from apps.product.models import Product
from apps.product.services.dtos import BuyProductIn, BuyProductOut
from config.container import container

if TYPE_CHECKING:
    from apps.customer.models import Customer


@final
@dataclass(kw_only=True, slots=True, frozen=True)
class BuyProductService:
    product: BuyProductIn

    @log_service_error
    def __call__(self, *, customer: Customer) -> BuyProductOut:
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
                product=dict(id=product.pk, count=self.product.count),
            )
        if customer.can_buy_max_count_of(product) < self.product.count:
            raise NotEnoughBalance(
                product=dict(id=product.pk, count=product.count, price=product.price),
                customer=dict(id=customer.pk, balance=customer.balance),
            )
        return self._buy(product=product, customer=customer)

    @transaction.atomic
    def _buy(self, *, product: Product, customer: Customer) -> BuyProductOut:
        customer.balance -= product.calculate_total_price(self.product.count)
        customer.save(update_fields=["balance"])
        product.count -= self.product.count
        product.save(update_fields=["count"])
        self._send_sms()
        return BuyProductOut(
            product=self.product.id,
            count=self.product.count,
            balance=customer.balance,
        )

    def _send_sms(self) -> None:
        container.resolve("SendSmsService")()


def buy_product_service_factory(product: dict) -> BuyProductService:
    return BuyProductService(product=BuyProductIn(**product))


container.register("BuyProductService", factory=buy_product_service_factory)
