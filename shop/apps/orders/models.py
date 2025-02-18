from django.db import models
from django.conf import settings
from django.core.validators import MaxValueValidator

class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='orders',
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
    )
    shipping_address = models.TextField()
    billing_address = models.TextField(null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def get_total_price(self):
        return sum(item.get_subtotal() for item in self.items.all())
    
    def save(self, *args, **kwargs):
        if not self.total_price:
            self.total_price = self.get_total_price()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f'Order {self.id} by {self.user.email}'

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='items'
    )
    product = models.ForeignKey(
        'products.Product', 
        on_delete=models.PROTECT, 
        related_name='order_items'
    )
    quantity = models.PositiveIntegerField(default=1, validators=[MaxValueValidator(100)])
    price = models.DecimalField(  # Store price at time of purchase
        max_digits=10,
        decimal_places=2,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def get_subtotal(self):
        return self.price * self.quantity
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name} in order {self.order.id}"
