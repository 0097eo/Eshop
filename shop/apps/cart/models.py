from django.db import models
from django.conf import settings
from django.core.validators import MaxValueValidator


class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_total_price(self):
        return sum(item.get_subtotal() for item in self.items.all())
    
    def __str__(self):
        return f'Cart for {self.user.email}'
    

class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MaxValueValidator(100)],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['cart', 'product']
        ordering = ['-created_at']

    def get_subtotal(self):
        return self.product.price * self.quantity
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name} in cart {self.cart.id}"