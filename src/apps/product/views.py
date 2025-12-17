from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.product.serializers import BuyProductSerializer
from apps.product.services import BuyProductService


class BuyProductView(APIView):
    def post(self, request: Request) -> Response:
        serializer = BuyProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        BuyProductService()(
            customer=request.user.customer,
            product_id=data.get("product_id"),
        )

        return Response(
            data={"message": "Thank you for buying!"},
            status=status.HTTP_200_OK,
        )
