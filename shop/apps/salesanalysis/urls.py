from django.urls import path
from . import views

urlpatterns = [
    # Daily Sales URLs
    path('daily-sales/', views.DailySalesListView.as_view(), name='daily-sales-list'),
    path('daily-sales/<int:pk>/', views.DailySalesDetailView.as_view(), name='daily-sales-detail'),
    path('daily-sales/report/', views.DailySalesReportView.as_view(), name='daily-sales-report'),
    
    # Product Performance URLs
    path('product-performance/', views.ProductPerformanceListView.as_view(), name='product-performance-list'),
    path('product-performance/<int:pk>/', views.ProductPerformanceDetailView.as_view(), name='product-performance-detail'),
    path('product-performance/report/', views.ProductPerformanceReportView.as_view(), name='product-performance-report'),
    
    # Category Performance URLs
    path('category-performance/', views.CategoryPerformanceListView.as_view(), name='category-performance-list'),
    path('category-performance/<int:pk>/', views.CategoryPerformanceDetailView.as_view(), name='category-performance-detail'),
    path('category-performance/report/', views.CategoryPerformanceReportView.as_view(), name='category-performance-report'),
    
    # Customer Insight URLs
    path('customer-insights/', views.CustomerInsightListView.as_view(), name='customer-insight-list'),
    path('customer-insights/<int:pk>/', views.CustomerInsightDetailView.as_view(), name='customer-insight-detail'),
    path('customer-insights/generate/', views.CustomerInsightGeneratorView.as_view(), name='customer-insight-generate'),
    
    # Sales Report URLs
    path('sales-reports/', views.SalesReportListView.as_view(), name='sales-report-list'),
    path('sales-reports/<int:pk>/', views.SalesReportDetailView.as_view(), name='sales-report-detail'),
    path('sales-reports/generate/', views.SalesReportGeneratorView.as_view(), name='sales-report-generate'),
    path('update-metrics/', views.UpdateSalesMetricsView.as_view(), name='update_sales_metrics'),
]