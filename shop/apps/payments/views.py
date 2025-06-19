import stripe
import requests
import base64
import datetime
import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import Payment
from ..accounts.permissions import IsCustomer
from ..orders.models import Order

stripe.api_key = settings.STRIPE_SECRET_KEY
logger = logging.getLogger(__name__)

class StripePaymentView(APIView):
    permission_classes = [IsCustomer]

    def post(self, request):
        order_id = request.data.get("order_id")
        if not order_id:
            return Response({"error": "order_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user

        # 1. Get the order, ensuring it belongs to the user
        order = get_object_or_404(Order, id=order_id, user=user)

        # 2. Check if the order is in the correct state to be paid for
        if order.status != 'PENDING':
            return Response(
                {"error": f"This order cannot be paid for. Its status is '{order.status}'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3. Check if a payment has already been initiated to prevent duplicates
        if Payment.objects.filter(order=order, status='pending').exists():
            return Response(
                {"error": "A payment process has already been initiated for this order."},
                status=status.HTTP_409_CONFLICT
            )

        amount = float(order.total_price)

        try:
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100), # Amount in cents
                currency="kes",
                payment_method_types=["card"],
                metadata={'order_id': order.id} # Securely link the intent to our order
            )

            # Create our internal payment record
            Payment.objects.create(
                user=user,
                order=order,
                amount=amount,
                payment_method="stripe",
                transaction_id=intent.id,
                status="pending",
            )

            return Response({
                "client_secret": intent.client_secret,
                "amount": amount
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Stripe Payment Intent creation failed for order {order_id}: {e}")
            return Response({"error": "An error occurred while communicating with Stripe."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        logger.warning(f"Stripe webhook signature/payload error: {e}")
        return JsonResponse({'error': 'Invalid payload or signature'}, status=400)

    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        transaction_id = payment_intent.id
        
        try:
            # Use the transaction_id from the intent to find our pending payment
            with transaction.atomic():
                payment = Payment.objects.select_for_update().get(transaction_id=transaction_id, status='pending')
                order = payment.order
                
                # Idempotency check: if order is no longer pending, we've likely processed it already.
                if order.status != 'PENDING':
                    logger.info(f"Stripe webhook for already processed order {order.id} received.")
                    return JsonResponse({'status': 'success', 'message': 'Order already processed'})

                # Update statuses
                payment.status = 'completed'
                order.status = 'PROCESSING' # Update order status to show it's paid
                
                payment.save()
                order.save()

                # You can send a "payment received" email here
                # send_payment_confirmation_email(order)

        except Payment.DoesNotExist:
            logger.error(f"Stripe webhook: Payment with transaction_id {transaction_id} not found.")
            return JsonResponse({'error': 'Payment record not found'}, status=404)
        except Exception as e:
            logger.error(f"Error processing Stripe webhook for {transaction_id}: {e}")
            return JsonResponse({'error': 'Internal server error'}, status=500)

    return JsonResponse({'status': 'success'})

class MpesaPaymentView(APIView):
    permission_classes = [IsCustomer]

    def get_access_token(self):
        auth_url = f"{settings.MPESA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials"
        response = requests.get(auth_url, auth=(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET))
        return response.json().get("access_token")

    def post(self, request):
        order_id = request.data.get("order_id")
        phone = request.data.get("phone")
        if not all([order_id, phone]):
            return Response({"error": "order_id and phone are required"}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        order = get_object_or_404(Order, id=order_id, user=user)

        if order.status != 'PENDING':
            return Response(
                {"error": f"This order cannot be paid for. Its status is '{order.status}'."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if Payment.objects.filter(order=order, status='pending').exists():
            return Response(
                {"error": "A payment process has already been initiated for this order."},
                status=status.HTTP_409_CONFLICT
            )

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
            "CallBackURL": "https://a203-105-163-0-243.ngrok-free.app/payments/mpesa/callback/",
            "AccountReference": f"Order_{order_id}",
            "TransactionDesc": f"Payment for order {order_id}",
        }

        # Send M-Pesa STK Push request
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        response = requests.post(f"{settings.MPESA_BASE_URL}/mpesa/stkpush/v1/processrequest", json=payload, headers=headers)

        if response.status_code == 200:
            data = response.json()
            checkout_request_id = data.get("CheckoutRequestID")

            # Create Payment record
            Payment.objects.create(
                user=user,
                order=order,
                amount=amount,
                payment_method="mpesa",
                mpesa_checkout_id=checkout_request_id,
                status="pending",
            )

            return Response({"message": "Payment initiated", "checkout_request_id": checkout_request_id}, status=status.HTTP_200_OK)

        return Response({"error": "Failed to initiate payment"}, status=status.HTTP_400_BAD_REQUEST)
    
@csrf_exempt
def mpesa_callback(request):
    
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            stk_callback = data.get("Body", {}).get("stkCallback", {})
            checkout_request_id = stk_callback.get("CheckoutRequestID")

            with transaction.atomic():
                payment = Payment.objects.select_for_update().get(mpesa_checkout_id=checkout_request_id, status='pending')
                order = payment.order

                if stk_callback.get("ResultCode") == 0:
                    if order.status != 'PENDING':
                        logger.info(f"M-Pesa callback for already processed order {order.id} received.")
                        return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})
                    metadata = stk_callback.get("CallbackMetadata", {}).get("Item", [])
                    receipt_number = next((item['Value'] for item in metadata if item['Name'] == 'MpesaReceiptNumber'), None)

                    payment.status = 'completed'
                    payment.transaction_id = receipt_number # This is the final transaction ID
                    order.status = 'PROCESSING'
                
                    payment.save()
                    order.save()
                else:
                    payment.status = 'failed'
                    payment.extra_data = {'error_message': stk_callback.get('ResultDesc')}
                    payment.save()

            return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})
        
        except Payment.DoesNotExist:
            logger.warning(f"M-Pesa callback for unknown CheckoutRequestID: {checkout_request_id}")
            return JsonResponse({"ResultCode": 1, "ResultDesc": "No matching transaction found"})
        
        except Exception as e:
            logger.error(f"M-Pesa callback internal error: {e}")
            return JsonResponse({"ResultCode": 1, "ResultDesc": "Internal Server Error"}, status=500)
