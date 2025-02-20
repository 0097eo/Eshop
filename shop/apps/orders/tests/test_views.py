from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from ..models import Order
from unittest.mock import patch

class OrderViewsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            email='test@test.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.order = Order.objects.create(
            id = 1,
            user=self.user,
            status='PENDING',
            shipping_address='123 Test St',
            billing_address='123 Test St'
        )

    def test_list_orders(self):
        url = reverse('order-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    @patch('apps.orders.serializers.CreateOrderFromCartSerializer.is_valid')
    @patch('apps.orders.serializers.CreateOrderFromCartSerializer.save')
    def test_create_order_from_cart(self, mock_save, mock_is_valid):
        mock_is_valid.return_value = True
        mock_save.return_value = self.order
        
        url = reverse('order-create')
        response = self.client.post(url, {})
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_order_detail(self):
        url = reverse('order-detail', kwargs={'pk': self.order.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.order.pk)

    def test_update_order_address(self):
        url = reverse('order-address-update', kwargs={'pk': self.order.pk})
        new_address = '456 New St'
        data = {
            'shipping_address': new_address,
            'billing_address': new_address
        }
        response = self.client.put(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['shipping_address'], new_address)
        self.assertEqual(response.data['billing_address'], new_address)

    @patch('apps.orders.views.send_order_status_update_email')
    def test_update_order_status(self, mock_email):
        url = reverse('order-status-update', kwargs={'pk': self.order.pk})
        data = {'status': 'PROCESSING'}
        response = self.client.put(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'PROCESSING')
        mock_email.assert_called_once()

    def test_delete_pending_order(self):
        url = reverse('order-delete', kwargs={'pk': self.order.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_non_pending_order(self):
        self.order.status = 'PROCESSING'
        self.order.save()
        
        url = reverse('order-delete', kwargs={'pk': self.order.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthorized_access(self):
        self.client.force_authenticate(user=None)
        url = reverse('order-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)