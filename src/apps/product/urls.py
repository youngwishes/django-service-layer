from django.urls import path

from apps.product.views import BuyProductView

urlpatterns = [
    path("", BuyProductView.as_view(), name="buy-product"),
]
