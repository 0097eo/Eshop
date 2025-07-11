from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.products.models import Product
from ..models import Order, OrderItem

class OrderModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='testuser@example.com', password='password123'
        )
        self.product = Product.objects.create(
            name='Test Product', price=Decimal('10.00')
        )
        self.order = Order.objects.create(
            id = 1,
            user=self.user,
            shipping_address='123 Test Street',
            billing_address='456 Billing Street',
            total_price=Decimal('0.00')
        )
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            price=self.product.price
        )

    def test_order_creation(self):
        self.assertEqual(self.order.user, self.user)
        self.assertEqual(self.order.status, 'PENDING')
        self.assertEqual(self.order.shipping_address, '123 Test Street')
        self.assertEqual(self.order.billing_address, '456 Billing Street')

    def test_order_total_price_calculation(self):
        expected_total = self.order_item.get_subtotal()
        self.assertEqual(self.order.get_total_price(), expected_total)

    def test_order_str_representation(self):
        self.assertEqual(str(self.order), f'Order {self.order.id} by {self.user.email}')

    def test_order_save_updates_total_price(self):
        self.order.save()
        self.assertEqual(self.order.total_price, self.order.get_total_price())

class OrderItemModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='testuser@example.com', password='password123'
        )
        self.product = Product.objects.create(
            name='Test Product', price=Decimal('10.00')
        )
        self.order = Order.objects.create(
            id = 1,
            user=self.user,
            shipping_address='123 Test Street',
            total_price=Decimal('0.00')
        )
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=3,
            price=self.product.price
        )

    def test_order_item_creation(self):
        self.assertEqual(self.order_item.order, self.order)
        self.assertEqual(self.order_item.product, self.product)
        self.assertEqual(self.order_item.quantity, 3)
        self.assertEqual(self.order_item.price, Decimal('10.00'))

    def test_order_item_subtotal(self):
        expected_subtotal = Decimal('30.00')  # 3 * 10.00
        self.assertEqual(self.order_item.get_subtotal(), expected_subtotal)

    def test_order_item_str_representation(self):
        self.assertEqual(str(self.order_item), f'3x {self.product.name} in order {self.order.id}')
