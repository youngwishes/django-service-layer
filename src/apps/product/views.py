from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.product.services.dtos import BuyProductIn
from apps.product.permissions import CustomerRequired
from apps.product.serializers import BuyProductSerializer
from apps.product.services import BuyProductService


class BuyProductView(APIView):
    permission_classes = (CustomerRequired,)

    def post(self, request: Request) -> Response:
        serializer = BuyProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        result = BuyProductService(
            product=BuyProductIn(
                id=data.get("id"),
                count=data.get("count"),
            ),
            customer=request.user.customer,
        )()

        return Response(
            data=result.asdict(),
            status=status.HTTP_200_OK,
        )
