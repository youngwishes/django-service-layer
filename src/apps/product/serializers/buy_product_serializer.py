from rest_framework import serializers


class BuyProductSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
