from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Order
from .serializers import OrderSerializer, CreateOrderFromCartSerializer
from .utils import send_order_status_update_email, send_shipping_confirmation_email

class OrderListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """List all orders for the authenticated user"""
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    

class OrderCreateFromCartView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Create a new order from cart"""
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


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        """Retrieve a specific order"""
        order = get_object_or_404(Order, pk=pk, user=request.user)
        serializer = OrderSerializer(order)
        return Response(serializer.data)


class OrderAddressUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    
    def put(self, request, pk):
        """Update order shipping and billing addresses"""
        order = get_object_or_404(Order, pk=pk, user=request.user)
        
        if order.status != 'PENDING':
            return Response(
                {'error': 'Can only update addresses for pending orders'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if 'shipping_address' in request.data:
            order.shipping_address = request.data['shipping_address']
        
        if 'billing_address' in request.data:
            order.billing_address = request.data['billing_address']
        
        order.save()
        
        serializer = OrderSerializer(order)
        return Response(serializer.data)
    

class OrderStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    
    def put(self, request, pk):
        """Update order status and send email notification"""
        order = get_object_or_404(Order, pk=pk, user=request.user)
        
        if 'status' not in request.data:
            return Response(
                {'error': 'Status field is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if request.data['status'] not in dict(Order.STATUS_CHOICES):
            return Response(
                {'error': 'Invalid status value'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        old_status = order.status
        order.status = request.data['status']
        order.save()
        
        # Send status update email
        if old_status != order.status:
            send_order_status_update_email(order)
            
            # Send additional shipping email if status is SHIPPED
            if order.status == 'SHIPPED':
                tracking_number = request.data.get('tracking_number')
                send_shipping_confirmation_email(order, tracking_number)
        
        serializer = OrderSerializer(order)
        return Response(serializer.data)
    
class OrderDeleteView(APIView):
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, pk):
        """Delete an order (only if it's in PENDING status)"""
        order = get_object_or_404(Order, pk=pk, user=request.user)
        
        if order.status != 'PENDING':
            return Response(
                {'error': 'Can only delete pending orders'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
