from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.salesanalysis.models import SalesRecord
from apps.orders.models import Order

class SalesViewsTest(APITestCase):
    def setUp(self):
        """Set up test data, including users and sample orders."""
        self.admin_user = get_user_model().objects.create_user(
            email="admin@example.com",
            password="adminpassword",
            user_type="ADMIN",  # Ensure this matches your model
            is_staff=True  # Make sure it's an admin
        )

        self.regular_user = get_user_model().objects.create_user(
            email="user@example.com",
            password="userpassword",
            user_type="CUSTOMER",  # Ensure this is a non-admin type
            is_staff=False  # Ensure not an admin
        )

        self.order = Order.objects.create(
            user=self.regular_user,
            status="PENDING",
            shipping_address="123 Street, City",
            billing_address="123 Street, City",
            total_price=100.00
        )

        self.sales_record = SalesRecord.objects.create(
            order=self.order,
            total_amount=100.00
        )

    def test_sales_list_view_authorized(self):
        """Ensure admin users can access sales list."""
        self.client.force_authenticate(user=self.admin_user)  # Authenticate as admin

        url = reverse("sales-list")  # Ensure this matches your urlpatterns
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total_amount", response.data[0])  # Check response structure

    def test_sales_list_view_unauthorized(self):
        """Ensure non-admin users cannot access sales list."""
        self.client.force_authenticate(user=self.regular_user)  # Authenticate as non-admin

        url = reverse("sales-list")
        response = self.client.get(url)

        print("Response Status Code:", response.status_code)  # Debugging
        print("Response Data:", response.data)  # Debugging

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_sales_report_view_authorized(self):
        """Ensure admin users can access sales report."""
        self.client.force_authenticate(user=self.admin_user)

        url = reverse("sales-report")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total_sales", response.data)

    def test_sales_report_view_unauthorized(self):
        """Ensure non-admin users cannot access sales report."""
        self.client.force_authenticate(user=self.regular_user)

        url = reverse("sales-report")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

