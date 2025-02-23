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
        amount = request.data.get("amount")
        user = request.user  # Ensure authentication

        order = get_object_or_404(Order, id=order_id)

        try:
            intent = stripe.PaymentIntent.create(
                amount=int(float(amount) * 100),  # Convert to cents
                currency="usd",
                payment_method_types=["card"],
            )

            payment = Payment.objects.create(
                user=user,
                order=order,
                amount=amount,
                payment_method="stripe",
                transaction_id=intent.id,
                status="pending",
            )

            return Response({"client_secret": intent.client_secret}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
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
        amount = request.data.get("amount")
        user = request.user  # Ensure authentication

        order = get_object_or_404(Order, id=order_id)

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
            "Amount": amount,
            "PartyA": phone,
            "PartyB": settings.MPESA_SHORTCODE,
            "PhoneNumber": phone,
            "CallBackURL": "https://callback-url.com/mpesa/callback",
            "AccountReference": "Eshop Payment",
            "TransactionDesc": "Payment for order",
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

            return Response({"message": "Payment initiated", "transaction_id": transaction_id}, status=status.HTTP_200_OK)

        return Response({"error": "Failed to initiate payment"}, status=status.HTTP_400_BAD_REQUEST)
    
@csrf_exempt
def mpesa_callback(request):
    if request.method == "POST":
        try:
            mpesa_response = json.loads(request.body.decode("utf-8"))

            # Extracting necessary data
            body = mpesa_response.get("Body", {})
            stk_callback = body.get("stkCallback", {})
            result_code = stk_callback.get("ResultCode", "")
            result_desc = stk_callback.get("ResultDesc", "")
            merchant_request_id = stk_callback.get("MerchantRequestID", "")
            checkout_request_id = stk_callback.get("CheckoutRequestID", "")

            # Check if the payment was successful
            if result_code == 0:
                # Successful payment
                callback_metadata = stk_callback.get("CallbackMetadata", {}).get("Item", [])

                # Extract transaction details
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

                # Save transaction to the database
                payment = Payment.objects.create(
                    transaction_id=transaction_id,
                    amount=amount,
                    payment_method="mpesa",
                    status="completed"
                )
                payment.save()

                return JsonResponse({"message": "Payment successful", "transaction_id": transaction_id}, status=200)

            else:
                # Failed transaction
                return JsonResponse({"message": "Payment failed", "error": result_desc}, status=400)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"message": "Invalid request"}, status=400)
