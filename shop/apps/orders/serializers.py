from rest_framework import serializers, status
from rest_framework.response import Response
from .models import Order, OrderItem
from django.db import transaction
from rest_framework.decorators import api_view


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        source='price',
        read_only=True
    )
    product_image = serializers.ImageField(source='product.image', read_only=True)
    subtotal = serializers.DecimalField(
        source='get_subtotal',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_price', 'product_image', 'quantity', 'subtotal']
        read_only_fields = ['id', 'product_price', 'product_image']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    status = serializers.CharField(read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user_email', 'items', 'total_price', 'status', 'shipping_address', 
                  'billing_address', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CreateOrderFromCartSerializer(serializers.Serializer):
    shipping_address = serializers.CharField()
    billing_address = serializers.CharField()

    @transaction.atomic
    def create(self, validated_data):
        user = self.context['request'].user
        cart = user.cart
        
        if not cart.items.exists():
            raise serializers.ValidationError({"error": "Cart is empty"})

        # Create order
        order = Order.objects.create(
            user=user,
            shipping_address=validated_data['shipping_address'],
            billing_address=validated_data['billing_address'],
            total_price=cart.get_total_price()
        )

        # Create order items from cart items
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )

        # Clear the cart
        cart.items.all().delete()

        return order

@api_view(['POST'])
def create_order_from_cart(request):
    serializer = CreateOrderFromCartSerializer(
        data=request.data,
        context={'request': request}
    )
    if serializer.is_valid():
        order = serializer.save()
        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)