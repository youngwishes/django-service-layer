from django.db import models


class Product(models.Model):
    title = models.CharField("название товара")
    price = models.PositiveIntegerField("цена товара")

    def __str__(self) -> str:
        return str(self.title)

    class Meta:
        verbose_name = "товар"
        verbose_name_plural = "Товары"
