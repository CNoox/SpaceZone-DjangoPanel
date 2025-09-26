from rest_framework import serializers
from .models import Order,OrderItem


class OrderSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = '__all__'

    def get_items(self,obj):
        return OrderItemSerializer(instance=obj.item.all(),many=True).data

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'
        extra_kwargs = {
            'product': {'required': True},
            'order': {'required': False},
        }