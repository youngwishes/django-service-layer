from decimal import Decimal

from django.db import models

from apps.product.enums import ProductStatusEnum


class Product(models.Model):
    title = models.CharField("наименование товара", max_length=256)
    price = models.PositiveIntegerField("цена товара")
    count = models.PositiveIntegerField("остаток на складе", default=0)
    status = models.PositiveSmallIntegerField(
        "статус товара",
        choices=ProductStatusEnum.choices(),
        default=ProductStatusEnum.AVAILABLE,
    )

    @property
    def is_available(self) -> bool:
        return self.status == ProductStatusEnum.AVAILABLE and self.count > 0

    def calculate_total_price(self, count: int) -> Decimal:
        return Decimal(count) * Decimal(self.price)

    def __str__(self) -> str:
        return str(self.title)

    class Meta:
        verbose_name = "товар"
        verbose_name_plural = "Товары"
