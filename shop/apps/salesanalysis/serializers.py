from rest_framework import serializers
from .models import DailySales, ProductPerformance, CategoryPerformance, CustomerInsight, SalesReport
from ..products.models import Product, Category

class DailySalesSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailySales
        fields = '__all__'

class ProductPerformanceSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_category = serializers.CharField(source='product.category.name', read_only=True)
    
    class Meta:
        model = ProductPerformance
        fields = ('id', 'date', 'product', 'product_name', 'product_category', 
                  'units_sold', 'revenue', 'average_rating')

class CategoryPerformanceSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = CategoryPerformance
        fields = ('id', 'date', 'category', 'category_name', 'products_sold', 'revenue')

class CustomerInsightSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    recency = serializers.SerializerMethodField()
    preferred_category_name = serializers.CharField(source='preferred_category.name', read_only=True)
    
    class Meta:
        model = CustomerInsight
        fields = ('id', 'user', 'user_email', 'user_name', 'total_spent', 'orders_count', 
                  'average_order_value', 'first_purchase_date', 'last_purchase_date', 
                  'preferred_category', 'preferred_category_name', 'recency')
    
    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    
    def get_recency(self, obj):
        days = obj.calculate_recency()
        if days is not None:
            return days
        return None

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'category', 'price')

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')

class SalesReportSerializer(serializers.ModelSerializer):
    top_products = ProductSerializer(many=True, read_only=True)
    top_categories = CategorySerializer(many=True, read_only=True)
    
    class Meta:
        model = SalesReport
        fields = ('id', 'report_type', 'start_date', 'end_date', 'total_sales', 
                  'total_orders', 'average_order_value', 'top_products', 'top_categories', 
                  'generated_at')