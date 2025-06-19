from django.conf import settings
from django.db import models

class Payment(models.Model):
    """
    Represents a payment transaction for an order.
    """
    PAYMENT_METHODS = [
        ("stripe", "Stripe"),
        ("mpesa", "M-Pesa"),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order = models.ForeignKey( "orders.Order", on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    transaction_id = models.CharField( max_length=100, unique=True, null=True, blank=True, help_text="The final, permanent transaction ID from Stripe (pi_...) or M-Pesa (receipt number)."
    )
    mpesa_checkout_id = models.CharField( max_length=100, unique=True, null=True, blank=True, help_text="The temporary CheckoutRequestID from an M-Pesa STK Push.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.id} for Order {self.order.id} ({self.status})"

    class Meta:
        ordering = ['-created_at']