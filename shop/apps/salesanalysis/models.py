from django.db import models
from django.utils import timezone
#from django.db.models import Sum, Count, Avg, F, Q
from django.contrib.auth import get_user_model

User = get_user_model()

class SalesMetric(models.Model):
    """Base model for various sales metrics"""
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class DailySales(SalesMetric):
    """Daily sales data"""
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    order_count = models.IntegerField(default=0)
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unique_customers = models.IntegerField(default=0)
    new_customers = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Daily Sales'
        verbose_name_plural = 'Daily Sales'
        ordering = ['-date']
        get_latest_by = 'date'

    def __str__(self):
        return f"Sales for {self.date.strftime('%Y-%m-%d')}"

class ProductPerformance(SalesMetric):
    """Product performance metrics"""
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='performance_metrics')
    units_sold = models.IntegerField(default=0)
    revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Product Performance'
        verbose_name_plural = 'Product Performance'
        ordering = ['-date', '-revenue']
        unique_together = ['date', 'product']

    def __str__(self):
        return f"{self.product.name} - {self.date.strftime('%Y-%m-%d')}"

class CategoryPerformance(SalesMetric):
    """Category performance metrics"""
    category = models.ForeignKey('products.Category', on_delete=models.CASCADE, related_name='performance_metrics')
    products_sold = models.IntegerField(default=0)
    revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = 'Category Performance'
        verbose_name_plural = 'Category Performance'
        ordering = ['-date', '-revenue']
        unique_together = ['date', 'category']

    def __str__(self):
        return f"{self.category.name} - {self.date.strftime('%Y-%m-%d')}"

class CustomerInsight(models.Model):
    """Customer buying patterns and insights"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='sales_insights')
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    orders_count = models.IntegerField(default=0)
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    first_purchase_date = models.DateField(null=True, blank=True)
    last_purchase_date = models.DateField(null=True, blank=True)
    preferred_category = models.ForeignKey('products.Category', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Customer Insight'
        verbose_name_plural = 'Customer Insights'
        ordering = ['-total_spent']

    def __str__(self):
        return f"Insights for {self.user.email}"

    def calculate_recency(self):
        """Calculate days since last purchase"""
        if self.last_purchase_date:
            today = timezone.now().date()
            return (today - self.last_purchase_date).days
        return None

class SalesReport(models.Model):
    """Generated sales reports"""
    REPORT_TYPES = (
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('QUARTERLY', 'Quarterly'),
        ('YEARLY', 'Yearly'),
        ('CUSTOM', 'Custom'),
    )
    
    report_type = models.CharField(max_length=10, choices=REPORT_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    total_sales = models.DecimalField(max_digits=12, decimal_places=2)
    total_orders = models.IntegerField()
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2)
    top_products = models.ManyToManyField('products.Product', related_name='top_in_reports')
    top_categories = models.ManyToManyField('products.Category', related_name='top_in_reports')
    generated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Sales Report'
        verbose_name_plural = 'Sales Reports'
        ordering = ['-generated_at']

    def __str__(self):
        return f"{self.get_report_type_display()} Report ({self.start_date} to {self.end_date})"