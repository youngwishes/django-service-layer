from rest_framework import serializers


class BuyProductSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    count = serializers.IntegerField()
