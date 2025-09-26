from django.shortcuts import render
from rest_framework import views,status
from rest_framework.response import Response
from .serializers import OrderSerializer,OrderItemSerializer
from .models import Order,OrderItem
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from product.models import Product

# Create your views here.

class OrderView(views.APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    def get(self,request):
        order = Order.objects.filter(user=request.user)
        if order.exists():
            ser_order = OrderSerializer(instance=order,many=True)
            return Response(ser_order.data,status=status.HTTP_200_OK)
        return None

class AddItemView(views.APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderItemSerializer
    def post(self,request):
        order, created = Order.objects.get_or_create(
            user=request.user,
            is_success=False
        )
        ser_item = OrderItemSerializer(data=request.data)
        if ser_item.is_valid():
            product = ser_item.validated_data['product']
            exist_item = order.item.filter(product=product).first()
            if not exist_item:
                ser_item.save(order=order,quantity=1)
                return Response(ser_item.data, status=status.HTTP_200_OK)
            if product.exist_number <= exist_item.quantity:
                return Response({'detail':f'You cannot add this item, you can only have {exist_item.quantity} of this item.'}, status=status.HTTP_400_BAD_REQUEST)
            exist_item.quantity += 1
            exist_item.save()
            return Response(OrderItemSerializer(instance=exist_item).data, status=status.HTTP_200_OK)
        return Response(ser_item.errors,status=status.HTTP_400_BAD_REQUEST)

class SubItemView(views.APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderItemSerializer
    def post(self,request):
        order, created = Order.objects.get_or_create(
            user=request.user,
            is_success=False
        )
        ser_item = OrderItemSerializer(data=request.data)
        if ser_item.is_valid():
            product = ser_item.validated_data['product']
            exist_item = order.item.filter(product=product).first()
            if not exist_item:
                return Response({'detail': 'Your item is not exist'}, status=status.HTTP_400_BAD_REQUEST)
            if  exist_item.quantity <= 1:
                exist_item.delete(  )
                return Response({'detail': 'Your item is deleted'}, status=status.HTTP_200_OK)
            exist_item.quantity -= 1
            exist_item.save()
            return Response(OrderItemSerializer(instance=exist_item).data, status=status.HTTP_200_OK)
        return Response(ser_item.errors,status=status.HTTP_400_BAD_REQUEST)

class DeleteItemView(views.APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderItemSerializer
    def delete(self,request,pk):
        product = Product.objects.filter(pk=pk).first()
        order = Order.objects.filter(user=request.user,is_success=False).first()
        item = OrderItem.objects.filter(product=product,order=order).first()
        if item:
            item.delete()
            return Response({'detail': 'Your item is deleted'}, status=status.HTTP_200_OK)
        return Response({'detail': 'Your item is not exist'}, status=status.HTTP_400_BAD_REQUEST)

