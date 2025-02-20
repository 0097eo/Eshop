from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from ..models import Cart, CartItem
from ...products.models import Product

class CartViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.product = Product.objects.create(
            name='Test Product',
            price=10.00,
            stock=5
        )

    def test_get_cart(self):
        response = self.client.get(reverse('cart'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['items']), 0)

    def test_add_to_cart(self):
        response = self.client.post(reverse('cart'), {
            'product_id': self.product.id,
            'quantity': 1
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['items']), 1)

    def test_add_invalid_quantity(self):
        response = self.client.post(reverse('cart'), {
            'product_id': self.product.id,
            'quantity': 0
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_clear_cart(self):
        CartItem.objects.create(
            cart=Cart.objects.create(user=self.user),
            product=self.product,
            quantity=1
        )
        response = self.client.delete(reverse('cart'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['items']), 0)

class CartItemViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.product = Product.objects.create(
            name='Test Product',
            price=10.00,
            stock=5
        )
        
        self.cart = Cart.objects.create(user=self.user)
        self.cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=1
        )

    def test_update_cart_item(self):
        response = self.client.put(
            reverse('cart-item', args=[self.cart_item.id]),
            {'quantity': 2}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.cart_item.refresh_from_db()
        self.assertEqual(self.cart_item.quantity, 2)

    def test_delete_cart_item_with_zero_quantity(self):
        response = self.client.put(
            reverse('cart-item', args=[self.cart_item.id]),
            {'quantity': 0}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CartItem.objects.filter(id=self.cart_item.id).exists(), False)

    def test_delete_cart_item(self):
        response = self.client.delete(
            reverse('cart-item', args=[self.cart_item.id])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CartItem.objects.filter(id=self.cart_item.id).exists(), False)