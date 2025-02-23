from django.db import models
from apps.orders.models import Order

class SalesRecord(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="sales")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sale {self.id} - {self.total_amount}"

