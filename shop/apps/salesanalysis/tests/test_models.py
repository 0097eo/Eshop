from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import timedelta, date
from ..models import DailySales, ProductPerformance, CategoryPerformance, CustomerInsight, SalesReport
from ...products.models import Product, Category

User = get_user_model()

class DailySalesModelTest(TestCase):
    def setUp(self):
        self.today = timezone.now().date()
        self.daily_sales = DailySales.objects.create(
            date=self.today,
            total_sales=Decimal('1250.75'),
            order_count=25,
            average_order_value=Decimal('50.03'),
            unique_customers=20,
            new_customers=5
        )

    def test_daily_sales_creation(self):
        """Test the creation of DailySales instance."""
        self.assertEqual(self.daily_sales.date, self.today)
        self.assertEqual(self.daily_sales.total_sales, Decimal('1250.75'))
        self.assertEqual(self.daily_sales.order_count, 25)
        self.assertEqual(self.daily_sales.average_order_value, Decimal('50.03'))
        self.assertEqual(self.daily_sales.unique_customers, 20)
        self.assertEqual(self.daily_sales.new_customers, 5)

    def test_str_method(self):
        """Test the string representation of DailySales."""
        self.assertEqual(str(self.daily_sales), f"Sales for {self.today.strftime('%Y-%m-%d')}")

    def test_daily_sales_ordering(self):
        """Test that DailySales is ordered by date descending."""
        yesterday = self.today - timedelta(days=1)
        tomorrow = self.today + timedelta(days=1)

        DailySales.objects.create(
            date=yesterday,
            total_sales= Decimal('500.00'),
            order_count=10,
        )

        DailySales.objects.create(
            date=tomorrow,
            total_sales= Decimal('2000.00'),
            order_count=40,
        )

        sales_list = list(DailySales.objects.all())
        self.assertEqual(sales_list[0].date, tomorrow)
        self.assertEqual(sales_list[1].date, self.today)
        self.assertEqual(sales_list[2].date, yesterday)

class ProductPerformanceModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(
            name="Test Product",
            price=Decimal('99.99'),
            category=self.category
        )
        self.today = timezone.now().date()
        self.product_performance = ProductPerformance.objects.create(
            date=self.today,
            product=self.product,
            units_sold=10,
            revenue=Decimal('999.90'),
            average_rating=Decimal('4.5')
        )

    def test_product_performance_creation(self):
        """Test that a ProductPerformance instance can be created with proper values"""
        self.assertEqual(self.product_performance.date, self.today)
        self.assertEqual(self.product_performance.product, self.product)
        self.assertEqual(self.product_performance.units_sold, 10)
        self.assertEqual(self.product_performance.revenue, Decimal('999.90'))
        self.assertEqual(self.product_performance.average_rating, Decimal('4.5'))

    def test_product_performance_str_representation(self):
        """Test the string representation of ProductPerformance"""
        expected_str = f"Test Product - {self.today.strftime('%Y-%m-%d')}"
        self.assertEqual(str(self.product_performance), expected_str)

    def test_product_performance_unique_together_constraint(self):
        """Test that product and date combination must be unique"""
        with self.assertRaises(Exception):
            ProductPerformance.objects.create(
                date=self.today,
                product=self.product,
                units_sold=15,
                revenue=Decimal('1500.00')
            )

class CategoryPerformanceModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test Category")
        self.today = timezone.now().date()
        self.category_performance = CategoryPerformance.objects.create(
            date=self.today,
            category=self.category,
            products_sold=25,
            revenue=Decimal('2500.00')
        )

    def test_category_performance_creation(self):
        """Test that a CategoryPerformance instance can be created with proper values"""
        self.assertEqual(self.category_performance.date, self.today)
        self.assertEqual(self.category_performance.category, self.category)
        self.assertEqual(self.category_performance.products_sold, 25)
        self.assertEqual(self.category_performance.revenue, Decimal('2500.00'))

    def test_category_performance_str_representation(self):
        """Test the string representation of CategoryPerformance"""
        expected_str = f"Test Category - {self.today.strftime('%Y-%m-%d')}"
        self.assertEqual(str(self.category_performance), expected_str)

    def test_category_performance_unique_together_constraint(self):
        """Test that category and date combination must be unique"""
        with self.assertRaises(Exception):
            CategoryPerformance.objects.create(
                date=self.today,
                category=self.category,
                products_sold=30,
                revenue=Decimal('3000.00')
            )


class CustomerInsightModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123'
        )
        self.category = Category.objects.create(name="Test Category")
        self.first_purchase = date(2023, 1, 1)
        self.last_purchase = date(2023, 3, 15)
        
        self.customer_insight = CustomerInsight.objects.create(
            user=self.user,
            total_spent=Decimal('1250.75'),
            orders_count=5,
            average_order_value=Decimal('250.15'),
            first_purchase_date=self.first_purchase,
            last_purchase_date=self.last_purchase,
            preferred_category=self.category
        )

    def test_customer_insight_creation(self):
        """Test that a CustomerInsight instance can be created with proper values"""
        self.assertEqual(self.customer_insight.user, self.user)
        self.assertEqual(self.customer_insight.total_spent, Decimal('1250.75'))
        self.assertEqual(self.customer_insight.orders_count, 5)
        self.assertEqual(self.customer_insight.average_order_value, Decimal('250.15'))
        self.assertEqual(self.customer_insight.first_purchase_date, self.first_purchase)
        self.assertEqual(self.customer_insight.last_purchase_date, self.last_purchase)
        self.assertEqual(self.customer_insight.preferred_category, self.category)

    def test_customer_insight_str_representation(self):
        """Test the string representation of CustomerInsight"""
        expected_str = f"Insights for test@example.com"
        self.assertEqual(str(self.customer_insight), expected_str)

    def test_calculate_recency(self):
        """Test calculation of days since last purchase (recency)"""
        today = timezone.now().date()
        days_since_purchase = (today - self.last_purchase).days
        self.assertEqual(self.customer_insight.calculate_recency(), days_since_purchase)
        
        # Test with no last purchase date
        self.customer_insight.last_purchase_date = None
        self.customer_insight.save()
        self.assertIsNone(self.customer_insight.calculate_recency())


class SalesReportModelTest(TestCase):
    def setUp(self):
        self.category1 = Category.objects.create(name="Category 1")
        self.category2 = Category.objects.create(name="Category 2")
        self.product1 = Product.objects.create(name="Product 1", price=Decimal('99.99'), category=self.category1)
        self.product2 = Product.objects.create(name="Product 2", price=Decimal('49.99'), category=self.category2)
        
        self.start_date = date(2023, 1, 1)
        self.end_date = date(2023, 1, 31)
        
        self.sales_report = SalesReport.objects.create(
            report_type='MONTHLY',
            start_date=self.start_date,
            end_date=self.end_date,
            total_sales=Decimal('5000.00'),
            total_orders=100,
            average_order_value=Decimal('50.00')
        )
        
        # Add many-to-many relationships
        self.sales_report.top_products.add(self.product1, self.product2)
        self.sales_report.top_categories.add(self.category1, self.category2)

    def test_sales_report_creation(self):
        """Test that a SalesReport instance can be created with proper values"""
        self.assertEqual(self.sales_report.report_type, 'MONTHLY')
        self.assertEqual(self.sales_report.start_date, self.start_date)
        self.assertEqual(self.sales_report.end_date, self.end_date)
        self.assertEqual(self.sales_report.total_sales, Decimal('5000.00'))
        self.assertEqual(self.sales_report.total_orders, 100)
        self.assertEqual(self.sales_report.average_order_value, Decimal('50.00'))
        
        # Test many-to-many relationships
        self.assertEqual(self.sales_report.top_products.count(), 2)
        self.assertEqual(self.sales_report.top_categories.count(), 2)
        self.assertIn(self.product1, self.sales_report.top_products.all())
        self.assertIn(self.product2, self.sales_report.top_products.all())
        self.assertIn(self.category1, self.sales_report.top_categories.all())
        self.assertIn(self.category2, self.sales_report.top_categories.all())

    def test_sales_report_str_representation(self):
        """Test the string representation of SalesReport"""
        expected_str = f"Monthly Report (2023-01-01 to 2023-01-31)"
        self.assertEqual(str(self.sales_report), expected_str)
        
    def test_sales_report_ordering(self):
        """Test that SalesReports are ordered by generated_at descending"""
        # Create another report
        new_report = SalesReport.objects.create(
            report_type='WEEKLY',
            start_date=date(2023, 2, 1),
            end_date=date(2023, 2, 7),
            total_sales=Decimal('2000.00'),
            total_orders=40,
            average_order_value=Decimal('50.00')
        )
        
        reports = list(SalesReport.objects.all())
        self.assertEqual(reports[0], new_report)  # Newer report should be first
        self.assertEqual(reports[1], self.sales_report)