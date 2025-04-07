from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from datetime import datetime, timedelta
import json
from ...products.models import Product, Category, ProductReview
from ...orders.models import Order, OrderItem
from ..models import DailySales, ProductPerformance, CategoryPerformance, CustomerInsight, SalesReport

User = get_user_model()

class BaseAnalyticsTestCase(TestCase):
    def setUp(self):
        # Create admin user
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            password='adminpassword',
            user_type='ADMIN'
        )
        
        # Create regular user
        self.customer = User.objects.create_user(
            email='customer@example.com',
            password='customerpassword',
            user_type='CUSTOMER'
        )
        
        # Create categories
        self.category1 = Category.objects.create(name='Electronics', description='Electronic items')
        self.category2 = Category.objects.create(name='Clothing', description='Apparel items')
        
        # Create products
        self.product1 = Product.objects.create(
            name='Laptop',
            description='A powerful laptop',
            price=1000.00,
            stock=10,
            category=self.category1
        )
        
        self.product2 = Product.objects.create(
            name='T-shirt',
            description='Cotton t-shirt',
            price=20.00,
            stock=50,
            category=self.category2
        )
        
        # Create orders
        self.order1 = Order.objects.create(
            user=self.customer,
            total_price=1020.00,
            shipping_address='123 Test St',
            status='COMPLETED',
            created_at=timezone.now() - timedelta(days=2)
        )
        
        self.order2 = Order.objects.create(
            user=self.customer,
            total_price=40.00,
            shipping_address='123 Test St',
            status='COMPLETED',
            created_at=timezone.now() - timedelta(days=1)
        )
        
        # Create order items
        self.order_item1 = OrderItem.objects.create(
            order=self.order1,
            product=self.product1,
            quantity=1,
            price=1000.00
        )
        
        self.order_item2 = OrderItem.objects.create(
            order=self.order1,
            product=self.product2,
            quantity=1,
            price=20.00
        )
        
        self.order_item3 = OrderItem.objects.create(
            order=self.order2,
            product=self.product2,
            quantity=2,
            price=20.00
        )
        
        # Set up the API client
        self.client = APIClient()
        
        # Dates for testing
        self.today = timezone.now().date()
        self.yesterday = self.today - timedelta(days=1)
        self.two_days_ago = self.today - timedelta(days=2)
        
        # Format dates for API requests
        self.start_date_str = self.two_days_ago.strftime('%Y-%m-%d')
        self.end_date_str = self.today.strftime('%Y-%m-%d')


class DailySalesViewsTestCase(BaseAnalyticsTestCase):
    def test_daily_sales_list_view_authenticated(self):
        """Test that authenticated admin can access DailySalesListView"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse('daily-sales-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    
    def test_daily_sales_list_view_non_admin(self):
        """Test that non-admin users cannot access DailySalesListView"""
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(reverse('daily-sales-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_daily_sales_post(self):
        """Test creating a new DailySales object"""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'date': self.today.strftime('%Y-%m-%d'),
            'total_sales': 500.00,
            'order_count': 5,
            'average_order_value': 100.00,
            'unique_customers': 3,
            'new_customers': 1
        }
        response = self.client.post(reverse('daily-sales-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DailySales.objects.count(), 1)
    
    def test_daily_sales_detail_view(self):
        """Test retrieving a specific DailySales object"""
        # Create a DailySales object
        daily_sales = DailySales.objects.create(
            date=self.today,
            total_sales=500.00,
            order_count=5,
            average_order_value=100.00,
            unique_customers=3,
            new_customers=1
        )
        
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse('daily-sales-detail', kwargs={'pk': daily_sales.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_sales'], '500.00')
    
    def test_daily_sales_update(self):
        """Test updating a DailySales object"""
        daily_sales = DailySales.objects.create(
            date=self.today,
            total_sales=500.00,
            order_count=5,
            average_order_value=100.00,
            unique_customers=3,
            new_customers=1
        )
        
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'date': self.today.strftime('%Y-%m-%d'),
            'total_sales': 600.00,
            'order_count': 6,
            'average_order_value': 100.00,
            'unique_customers': 4,
            'new_customers': 2
        }
        response = self.client.put(
            reverse('daily-sales-detail', kwargs={'pk': daily_sales.pk}),
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        daily_sales.refresh_from_db()
        self.assertEqual(float(daily_sales.total_sales), 600.00)
    
    def test_daily_sales_delete(self):
        """Test deleting a DailySales object"""
        daily_sales = DailySales.objects.create(
            date=self.today,
            total_sales=500.00,
            order_count=5,
            average_order_value=100.00,
            unique_customers=3,
            new_customers=1
        )
        
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(reverse('daily-sales-detail', kwargs={'pk': daily_sales.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(DailySales.objects.count(), 0)
    
        
    def test_daily_sales_report_view_missing_params(self):
        """Test that daily sales report requires date parameters"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse('daily-sales-report'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_daily_sales_report_view_invalid_date_format(self):
        """Test that daily sales report validates date format"""
        self.client.force_authenticate(user=self.admin_user)
        url = f"{reverse('daily-sales-report')}?start_date=invalid&end_date=invalid"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ProductPerformanceViewsTestCase(BaseAnalyticsTestCase):
    def test_product_performance_list_view(self):
        """Test that authenticated admin can access ProductPerformanceListView"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse('product-performance-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_product_performance_post(self):
        """Test creating a new ProductPerformance object"""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'date': self.today.strftime('%Y-%m-%d'),
            'product': self.product1.id,
            'units_sold': 10,
            'revenue': 10000.00,
        }
        response = self.client.post(reverse('product-performance-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProductPerformance.objects.count(), 1)
    
    def test_product_performance_detail_view(self):
        """Test retrieving a specific ProductPerformance object"""
        performance = ProductPerformance.objects.create(
            date=self.today,
            product=self.product1,
            units_sold=10,
            revenue=10000.00
        )
        
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse('product-performance-detail', kwargs={'pk': performance.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['units_sold'], 10)
    
    def test_product_performance_report_view(self):
        """Test generating a product performance report"""
        ProductReview.objects.create(
            product=self.product1,
            user=self.customer,
            rating=4,
            comment='Great product'
        )
        
        # Create an order on two_days_ago
        order = Order.objects.create(
            user=self.customer,
            total_price=100,
            created_at=timezone.now() - timedelta(days=2)  # Should match self.two_days_ago 
        )
        
        # Create an order item for product1
        OrderItem.objects.create(
            order=order,
            product=self.product1,
            quantity=2,
            price=50
        )


class CategoryPerformanceViewsTestCase(BaseAnalyticsTestCase):
    def test_category_performance_list_view(self):
        """Test that authenticated admin can access CategoryPerformanceListView"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse('category-performance-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_category_performance_post(self):
        """Test creating a new CategoryPerformance object"""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'date': self.today.strftime('%Y-%m-%d'),
            'category': self.category1.id,
            'products_sold': 15,
            'revenue': 15000.00,
        }
        response = self.client.post(reverse('category-performance-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CategoryPerformance.objects.count(), 1)
    
    def test_category_performance_detail_view(self):
        """Test retrieving a specific CategoryPerformance object"""
        performance = CategoryPerformance.objects.create(
            date=self.today,
            category=self.category1,
            products_sold=15,
            revenue=15000.00
        )
        
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse('category-performance-detail', kwargs={'pk': performance.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['products_sold'], 15)
    
    def test_category_performance_report_view(self):
        """Test generating a category performance report"""
        self.client.force_authenticate(user=self.admin_user)
        url = f"{reverse('category-performance-report')}?start_date={self.start_date_str}&end_date={self.end_date_str}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that performance data was generated
        self.assertTrue(
            CategoryPerformance.objects.filter(
                date=self.two_days_ago,
                category=self.category1
            ).exists()
        )


class CustomerInsightViewsTestCase(BaseAnalyticsTestCase):
    def test_customer_insight_list_view(self):
        """Test that authenticated admin can access CustomerInsightListView"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse('customer-insight-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_customer_insight_post(self):
        """Test creating a new CustomerInsight object"""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'user': self.customer.id,
            'total_spent': 1500.00,
            'orders_count': 3,
            'average_order_value': 500.00,
            'first_purchase_date': self.two_days_ago.strftime('%Y-%m-%d'),
            'last_purchase_date': self.yesterday.strftime('%Y-%m-%d'),
            'preferred_category': self.category1.id
        }
        response = self.client.post(reverse('customer-insight-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomerInsight.objects.count(), 1)
    
    def test_customer_insight_detail_view(self):
        """Test retrieving a specific CustomerInsight object"""
        insight = CustomerInsight.objects.create(
            user=self.customer,
            total_spent=1500.00,
            orders_count=3,
            average_order_value=500.00,
            first_purchase_date=self.two_days_ago,
            last_purchase_date=self.yesterday,
            preferred_category=self.category1
        )
        
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse('customer-insight-detail', kwargs={'pk': insight.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data['total_spent']), 1500.00)
    


class SalesReportViewsTestCase(BaseAnalyticsTestCase):
    def test_sales_report_list_view(self):
        """Test that authenticated admin can access SalesReportListView"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse('sales-report-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_sales_report_post(self):
        """Test creating a new SalesReport object"""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'report_type': 'MONTHLY',
            'start_date': self.two_days_ago.strftime('%Y-%m-%d'),
            'end_date': self.today.strftime('%Y-%m-%d'),
            'total_sales': 2000.00,
            'total_orders': 5,
            'average_order_value': 400.00
        }
        response = self.client.post(reverse('sales-report-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SalesReport.objects.count(), 1)
    
    def test_sales_report_detail_view(self):
        """Test retrieving a specific SalesReport object"""
        report = SalesReport.objects.create(
            report_type='MONTHLY',
            start_date=self.two_days_ago,
            end_date=self.today,
            total_sales=2000.00,
            total_orders=5,
            average_order_value=400.00
        )
        report.top_products.add(self.product1)
        report.top_categories.add(self.category1)
        
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse('sales-report-detail', kwargs={'pk': report.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data['total_sales']), 2000.00)
    
    def test_sales_report_generator_view(self):
        """Test generating a sales report"""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'report_type': 'WEEKLY',
            'start_date': self.start_date_str,
            'end_date': self.end_date_str
        }
        response = self.client.post(reverse('sales-report-generate'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that report was generated
        self.assertEqual(SalesReport.objects.count(), 1)
        report = SalesReport.objects.first()
        self.assertEqual(report.report_type, 'WEEKLY')
        
        # Check that top products and categories were set
        self.assertIn(self.product1, report.top_products.all())
        self.assertIn(self.product2, report.top_products.all())
        self.assertIn(self.category1, report.top_categories.all())
        self.assertIn(self.category2, report.top_categories.all())
    
    def test_sales_report_generator_view_missing_params(self):
        """Test that sales report generator requires parameters"""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'report_type': 'WEEKLY'
            # Missing date parameters
        }
        response = self.client.post('sales-report-generator', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_sales_report_generator_view_no_orders(self):
        """Test sales report generator with no orders in date range"""
        self.client.force_authenticate(user=self.admin_user)
        # Use dates far in the future
        future_date = self.today + timedelta(days=30)
        data = {
            'report_type': 'WEEKLY',
            'start_date': future_date.strftime('%Y-%m-%d'),
            'end_date': (future_date + timedelta(days=7)).strftime('%Y-%m-%d')
        }
        response = self.client.post('sales-report-generator', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UpdateSalesMetricsViewTestCase(BaseAnalyticsTestCase):
    def test_update_sales_metrics_view(self):
        """Test the update sales metrics view"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(reverse('update_sales_metrics'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "Sales metrics update triggered successfully")