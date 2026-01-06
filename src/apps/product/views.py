from __future__ import annotations

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.product.permissions import CustomerRequired
from apps.product.serializers import BuyProductSerializer
from config.container import container


class BuyProductView(APIView):
    permission_classes = (CustomerRequired,)

    def post(self, request: Request) -> Response:
        serializer = BuyProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = container.resolve(
            "BuyProductService",
            product=serializer.validated_data,
        )(customer=request.user.customer)

        return Response(
            data=result.asdict(),
            status=status.HTTP_200_OK,
        )
