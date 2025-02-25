import stripe
import requests
import base64
import datetime
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import Payment
from ..accounts.permissions import IsCustomer
from ..orders.models import Order

stripe.api_key = settings.STRIPE_SECRET_KEY

class StripePaymentView(APIView):
    permission_classes = [IsCustomer]
    def post(self, request):
        order_id = request.data.get("order_id")
        user = request.user

        # First check if order exists
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response(
                {"error": f"Order with ID {order_id} does not exist"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Then check if order belongs to user
        if order.user != user:
            return Response(
                {"error": "This order belongs to another user"},
                status=status.HTTP_403_FORBIDDEN
            )

        amount = float(order.total_price)

        try:
            # Check for existing pending payment
            existing_payment = Payment.objects.filter(
                order=order,
                status='pending'
            ).first()

            if existing_payment:
                return Response({
                    "error": "Payment already initiated for this order",
                    "payment_id": existing_payment.transaction_id
                }, status=status.HTTP_400_BAD_REQUEST)

            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),
                currency="kes",
                payment_method_types=["card"],
                metadata={
                    'order_id': order_id,
                    'user_id': str(user.id)
                }
            )

            payment = Payment.objects.create(
                user=user,
                order=order,
                amount=amount,
                payment_method="stripe",
                transaction_id=intent.id,
                status="pending",
            )

            return Response({"client_secret": intent.client_secret, "amount": amount}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )

        if event.type == 'payment_intent.succeeded':
            payment_intent = event.data.object
            order_id = payment_intent.metadata.get('order_id')
            user_id = payment_intent.metadata.get('user_id')
            
            if order_id and user_id:
                try:
                    # Verify order belongs to correct user and is in valid state
                    order = Order.objects.get(
                        id=order_id,
                        user_id=user_id,
                        status='pending'
                    )
                    
                    order.status = 'delivered'
                    order.save()

                    # Update payment status
                    payment = Payment.objects.get(
                        transaction_id=payment_intent.id,
                        order_id=order_id
                    )
                    payment.status = 'completed'
                    payment.save()

                except Order.DoesNotExist:
                    return JsonResponse({'error': 'Invalid order'}, status=400)
                except Payment.DoesNotExist:
                    return JsonResponse({'error': 'Invalid payment'}, status=400)

        return JsonResponse({'status': 'success'})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

class MpesaPaymentView(APIView):
    permission_classes = [IsCustomer]

    def get_access_token(self):
        auth_url = f"{settings.MPESA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials"
        response = requests.get(auth_url, auth=(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET))
        return response.json().get("access_token")

    def post(self, request):
        order_id = request.data.get("order_id")
        if not order_id:
            return Response({"error": "order_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        phone = request.data.get("phone")
        user = request.user

        # First check if order exists
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response(
                {"error": f"Order with ID {order_id} does not exist"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Then check if order belongs to user
        if order.user != user:
            return Response(
                {"error": "This order belongs to another user"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check for existing pending payment
        existing_payment = Payment.objects.filter(
            order=order,
            status='pending'
        ).first()

        if existing_payment:
            return Response({
                "error": "Payment already initiated for this order",
                "payment_id": existing_payment.transaction_id
            }, status=status.HTTP_400_BAD_REQUEST)

        amount = float(order.total_price)

        access_token = self.get_access_token()
        if not access_token:
            return Response({"error": "Failed to obtain access token"}, status=status.HTTP_400_BAD_REQUEST)

        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        password = base64.b64encode(f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}".encode()).decode()

        payload = {
            "BusinessShortCode": settings.MPESA_SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": phone,
            "PartyB": settings.MPESA_SHORTCODE,
            "PhoneNumber": phone,
            "CallBackURL": "https://callback-url.com/mpesa/callback",
            "AccountReference": f"Order_{order_id}",
            "TransactionDesc": f"Payment for order {order_id}",
        }

        # Send M-Pesa STK Push request
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        response = requests.post(f"{settings.MPESA_BASE_URL}/mpesa/stkpush/v1/processrequest", json=payload, headers=headers)

        if response.status_code == 200:
            data = response.json()
            transaction_id = data.get("CheckoutRequestID", "N/A")

            # Create Payment record
            Payment.objects.create(
                user=user,
                order=order,
                amount=amount,
                payment_method="mpesa",
                transaction_id=transaction_id,
                status="pending",
            )

            return Response({"message": "Payment initiated", "transaction_id": transaction_id, "amount": amount}, status=status.HTTP_200_OK)

        return Response({"error": "Failed to initiate payment"}, status=status.HTTP_400_BAD_REQUEST)
    
@csrf_exempt
def mpesa_callback(request):
    if request.method == "POST":
        try:
            mpesa_response = json.loads(request.body.decode("utf-8"))

            body = mpesa_response.get("Body", {})
            stk_callback = body.get("stkCallback", {})
            result_code = stk_callback.get("ResultCode", "")
            result_desc = stk_callback.get("ResultDesc", "")
            checkout_request_id = stk_callback.get("CheckoutRequestID", "")

            if result_code == 0:
                callback_metadata = stk_callback.get("CallbackMetadata", {}).get("Item", [])

                transaction_id = ""
                amount = 0
                phone_number = ""
                
                for item in callback_metadata:
                    name = item.get("Name")
                    if name == "MpesaReceiptNumber":
                        transaction_id = item.get("Value", "")
                    elif name == "Amount":
                        amount = item.get("Value", 0)
                    elif name == "PhoneNumber":
                        phone_number = item.get("Value", "")

                try:
                    # Find the payment record and verify order status
                    payment = Payment.objects.get(
                        transaction_id=checkout_request_id,
                        status='pending'
                    )
                    order = payment.order

                    # Verify order is still in pending state
                    if order.status != 'pending':
                        return JsonResponse({
                            "error": "Order already processed"
                        }, status=400)

                    # Update order status
                    order.status = 'delivered'
                    order.save()

                    # Update payment status
                    payment.status = "completed"
                    payment.transaction_id = transaction_id
                    payment.save()

                    return JsonResponse({
                        "message": "Payment successful",
                        "transaction_id": transaction_id
                    }, status=200)

                except Payment.DoesNotExist:
                    return JsonResponse({
                        "error": "Invalid payment record"
                    }, status=400)
                except Order.DoesNotExist:
                    return JsonResponse({
                        "error": "Invalid order"
                    }, status=400)

            else:
                # Failed transaction
                return JsonResponse({
                    "message": "Payment failed",
                    "error": result_desc
                }, status=400)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"message": "Invalid request"}, status=400)