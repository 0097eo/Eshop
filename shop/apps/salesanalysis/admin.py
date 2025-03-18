from django.contrib import admin
from .models import (
    DailySales, 
    ProductPerformance, 
    CategoryPerformance, 
    CustomerInsight, 
    SalesReport
)

@admin.register(DailySales)
class DailySalesAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_sales', 'order_count', 'average_order_value', 'unique_customers', 'new_customers')
    list_filter = ('date',)
    search_fields = ('date',)
    date_hierarchy = 'date'
    readonly_fields = ('average_order_value',)

@admin.register(ProductPerformance)
class ProductPerformanceAdmin(admin.ModelAdmin):
    list_display = ('date', 'product', 'units_sold', 'revenue', 'average_rating')
    list_filter = ('date', 'product__category')
    search_fields = ('product__name',)
    date_hierarchy = 'date'
    autocomplete_fields = ('product',)

@admin.register(CategoryPerformance)
class CategoryPerformanceAdmin(admin.ModelAdmin):
    list_display = ('date', 'category', 'products_sold', 'revenue')
    list_filter = ('date', 'category')
    search_fields = ('category__name',)
    date_hierarchy = 'date'
    autocomplete_fields = ('category',)

@admin.register(CustomerInsight)
class CustomerInsightAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_spent', 'orders_count', 'average_order_value', 
                   'first_purchase_date', 'last_purchase_date', 'preferred_category')
    list_filter = ('preferred_category', 'last_purchase_date')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('average_order_value', 'first_purchase_date', 'last_purchase_date')
    autocomplete_fields = ('user', 'preferred_category')

@admin.register(SalesReport)
class SalesReportAdmin(admin.ModelAdmin):
    list_display = ('report_type', 'start_date', 'end_date', 'total_sales', 
                   'total_orders', 'average_order_value', 'generated_at')
    list_filter = ('report_type', 'start_date', 'end_date', 'generated_at')
    search_fields = ('report_type',)
    readonly_fields = ('generated_at', 'average_order_value')
    filter_horizontal = ('top_products', 'top_categories')
    date_hierarchy = 'generated_at'
    
    fieldsets = (
        ('Report Information', {
            'fields': ('report_type', 'start_date', 'end_date', 'generated_at')
        }),
        ('Summary', {
            'fields': ('total_sales', 'total_orders', 'average_order_value')
        }),
        ('Top Performers', {
            'fields': ('top_products', 'top_categories')
        }),
    )