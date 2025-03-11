from rest_framework import serializers
from .models import Cart, CartItem

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(
        source='product.price',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    product_image = serializers.SerializerMethodField()
    subtotal = serializers.DecimalField(
        source='get_subtotal',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_name', 'product_image', 'product_price', 'quantity', 'subtotal']
        read_only_fields = ['id']
    
    def get_product_image(self, obj):
        return obj.product.image.url if obj.product.image and hasattr(obj.product.image, 'url') else None

    def get_product_image(self, obj):
        return obj.product.image.url if obj.product.image else None

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(
        source='get_total_price',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']