from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Cart, CartItem
from ..products.models import Product
from .serializers import CartSerializer, CartItemSerializer

class CartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_cart(self, user):
        cart, created = Cart.objects.get_or_create(
            user=user,
        )
        return cart
    
    def get(self, request):
        cart = self.get_cart(request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
    @transaction.atomic
    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        #validate product
        product = get_object_or_404(Product, id=product_id)

        if quantity < 1:
            return Response(
                {'error': 'Quantity must be at least 1'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            cart = self.get_cart(request.user)
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )

            if not created:
                cart_item.quantity += quantity
                cart_item.save()

            serializer = CartSerializer(cart)
            return Response(serializer.data)
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
    def delete(self, request):
        """Clear all items from the cart"""
        cart = Cart.objects.get(user=request.user)
        CartItem.objects.filter(cart=cart).delete()
        serializer = CartSerializer(cart)
        return Response(serializer.data)

class CartItemView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, item_id):
        cart_item = get_object_or_404(
            CartItem,
            id=item_id,
            cart__user=request.user,
        )
        
        quantity = int(request.data.get('quantity', 0))
        
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            serializer = CartSerializer(cart_item.cart)
            return Response(serializer.data)
        elif quantity == 0:
            cart_item.delete()
            serializer = CartSerializer(cart_item.cart)
            return Response(serializer.data)
        else:
            return Response(
                {'error': 'Quantity must be non-negative'},
                status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request, item_id):
        cart_item = get_object_or_404(
            CartItem,
            id=item_id,
            cart__user=request.user,
        )
        cart = cart_item.cart
        cart_item.delete()
        serializer = CartSerializer(cart)
        return Response(serializer.data)