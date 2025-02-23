from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.orders.models import Order
from apps.salesanalysis.models import SalesRecord

class SalesRecordModelTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = get_user_model().objects.create_user(
            email="testuser@example.com",
            password="securepassword"
        )

        # Create an order linked to the user
        self.order = Order.objects.create(
            user=self.user,
            status="PENDING",
            shipping_address="123 Test Street",
            billing_address="456 Billing Ave",
            total_price=500.00
        )

    def test_create_sales_record(self):
        """Test that a SalesRecord is created successfully."""
        sales_record = SalesRecord.objects.create(
            order=self.order,
            total_amount=500.00
        )

        self.assertEqual(sales_record.order, self.order)
        self.assertEqual(sales_record.total_amount, 500.00)
        self.assertIsNotNone(sales_record.date)

    def test_sales_record_str(self):
        """Test the string representation of SalesRecord."""
        sales_record = SalesRecord.objects.create(
            order=self.order,
            total_amount=350.75
        )

        self.assertEqual(str(sales_record), f"Sale {sales_record.id} - 350.75")
