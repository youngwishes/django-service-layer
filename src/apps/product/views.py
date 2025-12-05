from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response

from src.apps.product.exceptions import ProductDoesNotExist, NotEnoughBalance
from src.apps.product.serializers import BuyProductSerializer
from src.apps.product.services import BuyProductService


class BuyProductView(APIView):
    def post(self, request: Request) -> Response:
        try:
            # Validation
            serializer = BuyProductSerializer(request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data

            # Business logic
            response = BuyProductService()(
                customer=request.user.customer,
                product_id=data.get("product_id"),
            )
        except (ProductDoesNotExist, NotEnoughBalance) as exc:
            return Response(data={"error": exc.message}, status=status.HTTP_400_BAD_REQUEST)

        return Response(data=response, status=status.HTTP_200_OK)
