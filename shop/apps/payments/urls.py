from django.urls import path
from .views import StripePaymentView, MpesaPaymentView, mpesa_callback

urlpatterns = [
    path("stripe/", StripePaymentView.as_view(), name="stripe-payment"),
    path("mpesa/", MpesaPaymentView.as_view(), name="mpesa-payment"),
    path("mpesa/callback/", mpesa_callback, name="mpesa_callback"),
]
