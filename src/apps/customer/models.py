from django.contrib.auth.models import User
from django.db import models

class Customer(models.Model):
    user = models.OneToOneField(
        User,
        verbose_name="пользователь",
        on_delete=models.SET_NULL,
        related_name="customer",
        null=True,
        blank=True,
    )
    balance = models.PositiveIntegerField("количество рублей на балансе")

    class Meta:
        verbose_name = "заказчик"
        verbose_name_plural = "Заказчики"
