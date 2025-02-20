from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from ..models import Cart, CartItem
from ...products.models import Product

class CartTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.cart = Cart.objects.create(user=self.user)
        self.product = Product.objects.create(
            name='Test Product',
            price=10.00
        )

    def test_cart_creation(self):
        self.assertEqual(str(self.cart), f'Cart for {self.user.email}')
        self.assertTrue(self.cart.created_at)
        self.assertTrue(self.cart.updated_at)

    def test_cart_total_price(self):
        CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2
        )
        self.assertEqual(self.cart.get_total_price(), 20.00)

class CartItemTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.cart = Cart.objects.create(user=self.user)
        self.product = Product.objects.create(
            name='Test Product',
            price=10.00
        )
        self.cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2
        )

    def test_cart_item_creation(self):
        self.assertEqual(
            str(self.cart_item),
            f"2x Test Product in cart {self.cart.id}"
        )
        self.assertTrue(self.cart_item.created_at)
        self.assertTrue(self.cart_item.updated_at)

    def test_cart_item_subtotal(self):
        self.assertEqual(self.cart_item.get_subtotal(), 20.00)

    def test_cart_item_quantity_validation(self):
        self.cart_item.quantity = 101
        with self.assertRaises(ValidationError):
            self.cart_item.full_clean()

    def test_unique_cart_product_combination(self):
        with self.assertRaises(Exception):
            CartItem.objects.create(
                cart=self.cart,
                product=self.product,
                quantity=1
            )