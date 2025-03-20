from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..accounts.permissions import IsAdmin
from django.db.models import Sum, Avg, F
from django.utils import timezone
from datetime import datetime, timedelta
from .models import DailySales, ProductPerformance, CategoryPerformance, CustomerInsight, SalesReport
from .serializers import (
    DailySalesSerializer, ProductPerformanceSerializer, CategoryPerformanceSerializer,
    CustomerInsightSerializer, SalesReportSerializer
)

from ..products.models import Product, Category
from ..orders.models import Order, OrderItem

class DailySalesListView(APIView):
    permission_classes = [IsAdmin]
    
    def get(self, request):
        daily_sales = DailySales.objects.all().order_by('-date')
        serializer = DailySalesSerializer(daily_sales, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = DailySalesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DailySalesDetailView(APIView):
    permission_classes = [IsAdmin]
    
    def get_object(self, pk):
        try:
            return DailySales.objects.get(pk=pk)
        except DailySales.DoesNotExist:
            return None
            
    def get(self, request, pk):
        daily_sales = self.get_object(pk)
        if not daily_sales:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = DailySalesSerializer(daily_sales)
        return Response(serializer.data)
        
    def put(self, request, pk):
        daily_sales = self.get_object(pk)
        if not daily_sales:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = DailySalesSerializer(daily_sales, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request, pk):
        daily_sales = self.get_object(pk)
        if not daily_sales:
            return Response(status=status.HTTP_404_NOT_FOUND)
        daily_sales.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DailySalesReportView(APIView):
    permission_classes = [IsAdmin]
    
    def get(self, request):
        """Generate daily sales report for the given date range"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            return Response(
                {"error": "Both start_date and end_date are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Get orders in the date range
        orders = Order.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )
        
        # Get or create DailySales objects for each date in the range
        delta = end_date - start_date
        for i in range(delta.days + 1):
            current_date = start_date + timedelta(days=i)
            daily_orders = orders.filter(created_at__date=current_date)
            
            if daily_orders.exists():
                # Calculate metrics
                total_sales = daily_orders.aggregate(Sum('total_price'))['total_price__sum'] or 0
                order_count = daily_orders.count()
                average_order_value = total_sales / order_count if order_count > 0 else 0
                unique_customers = daily_orders.values('user').distinct().count()
                
                # Count new customers (first purchase on this date)
                new_customers = 0
                for order in daily_orders:
                    user_previous_orders = Order.objects.filter(
                        user=order.user,
                        created_at__date__lt=current_date
                    ).exists()
                    if not user_previous_orders:
                        new_customers += 1
                
                # Create or update DailySales
                daily_sales, created = DailySales.objects.update_or_create(
                    date=current_date,
                    defaults={
                        'total_sales': total_sales,
                        'order_count': order_count,
                        'average_order_value': average_order_value,
                        'unique_customers': unique_customers,
                        'new_customers': new_customers
                    }
                )
        
        # Return the generated data
        daily_sales_data = DailySales.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date')
        
        serializer = DailySalesSerializer(daily_sales_data, many=True)
        return Response(serializer.data)


class ProductPerformanceListView(APIView):
    permission_classes = [IsAdmin]
    
    def get(self, request):
        product_performance = ProductPerformance.objects.all().order_by('-date')
        serializer = ProductPerformanceSerializer(product_performance, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = ProductPerformanceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductPerformanceDetailView(APIView):
    permission_classes = [IsAdmin]
    
    def get_object(self, pk):
        try:
            return ProductPerformance.objects.get(pk=pk)
        except ProductPerformance.DoesNotExist:
            return None
            
    def get(self, request, pk):
        product_performance = self.get_object(pk)
        if not product_performance:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = ProductPerformanceSerializer(product_performance)
        return Response(serializer.data)
        
    def put(self, request, pk):
        product_performance = self.get_object(pk)
        if not product_performance:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = ProductPerformanceSerializer(product_performance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request, pk):
        product_performance = self.get_object(pk)
        if not product_performance:
            return Response(status=status.HTTP_404_NOT_FOUND)
        product_performance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductPerformanceReportView(APIView):
    permission_classes = [IsAdmin]
    
    def get(self, request):
        """Generate product performance report for the given date range"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            return Response(
                {"error": "Both start_date and end_date are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get all products
        products = Product.objects.all()
        
        # Get order items in the date range
        order_items = OrderItem.objects.filter(
            order__created_at__date__gte=start_date,
            order__created_at__date__lte=end_date
        )
        
        # Process each day in the range
        delta = end_date - start_date
        for i in range(delta.days + 1):
            current_date = start_date + timedelta(days=i)
            
            # Process each product
            for product in products:
                # Get order items for this product on this date
                product_items = order_items.filter(
                    product=product,
                    order__created_at__date=current_date
                )
                
                if product_items.exists():
                    units_sold = product_items.aggregate(Sum('quantity'))['quantity__sum'] or 0
                    revenue = sum(item.quantity * item.price for item in product_items)
                    
                    # Calculate average rating
                    from ..products.models import ProductReview
                    reviews = ProductReview.objects.filter(product=product)
                    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] if reviews.exists() else None
                    
                    # Create or update ProductPerformance
                    performance, created = ProductPerformance.objects.update_or_create(
                        date=current_date,
                        product=product,
                        defaults={
                            'units_sold': units_sold,
                            'revenue': revenue,
                            'average_rating': avg_rating
                        }
                    )
        
        # Return the generated data
        product_performance_data = ProductPerformance.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date', '-revenue')
        
        serializer = ProductPerformanceSerializer(product_performance_data, many=True)
        return Response(serializer.data)


class CategoryPerformanceListView(APIView):
    permission_classes = [IsAdmin]
    
    def get(self, request):
        category_performance = CategoryPerformance.objects.all().order_by('-date')
        serializer = CategoryPerformanceSerializer(category_performance, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = CategoryPerformanceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryPerformanceDetailView(APIView):
    permission_classes = [IsAdmin]
    
    def get_object(self, pk):
        try:
            return CategoryPerformance.objects.get(pk=pk)
        except CategoryPerformance.DoesNotExist:
            return None
            
    def get(self, request, pk):
        category_performance = self.get_object(pk)
        if not category_performance:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = CategoryPerformanceSerializer(category_performance)
        return Response(serializer.data)
        
    def put(self, request, pk):
        category_performance = self.get_object(pk)
        if not category_performance:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = CategoryPerformanceSerializer(category_performance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request, pk):
        category_performance = self.get_object(pk)
        if not category_performance:
            return Response(status=status.HTTP_404_NOT_FOUND)
        category_performance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoryPerformanceReportView(APIView):
    permission_classes = [IsAdmin]
    
    def get(self, request):
        """Generate category performance report for the given date range"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            return Response(
                {"error": "Both start_date and end_date are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get all categories
        categories = Category.objects.all()
        
        # Process each day in the range
        delta = end_date - start_date
        for i in range(delta.days + 1):
            current_date = start_date + timedelta(days=i)
            
            # Process each category
            for category in categories:
                # Get order items for products in this category on this date
                category_items = OrderItem.objects.filter(
                    product__category=category,
                    order__created_at__date=current_date
                )
                
                if category_items.exists():
                    products_sold = category_items.aggregate(Sum('quantity'))['quantity__sum'] or 0
                    revenue = sum(item.quantity * item.price for item in category_items)
                    
                    # Create or update CategoryPerformance
                    performance, created = CategoryPerformance.objects.update_or_create(
                        date=current_date,
                        category=category,
                        defaults={
                            'products_sold': products_sold,
                            'revenue': revenue
                        }
                    )
        
        # Return the generated data
        category_performance_data = CategoryPerformance.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date', '-revenue')
        
        serializer = CategoryPerformanceSerializer(category_performance_data, many=True)
        return Response(serializer.data)


class CustomerInsightListView(APIView):
    permission_classes = [IsAdmin]
    
    def get(self, request):
        customer_insights = CustomerInsight.objects.all().order_by('-total_spent')
        serializer = CustomerInsightSerializer(customer_insights, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = CustomerInsightSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerInsightDetailView(APIView):
    permission_classes = [IsAdmin]
    
    def get_object(self, pk):
        try:
            return CustomerInsight.objects.get(pk=pk)
        except CustomerInsight.DoesNotExist:
            return None
            
    def get(self, request, pk):
        customer_insight = self.get_object(pk)
        if not customer_insight:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = CustomerInsightSerializer(customer_insight)
        return Response(serializer.data)
        
    def put(self, request, pk):
        customer_insight = self.get_object(pk)
        if not customer_insight:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = CustomerInsightSerializer(customer_insight, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request, pk):
        customer_insight = self.get_object(pk)
        if not customer_insight:
            return Response(status=status.HTTP_404_NOT_FOUND)
        customer_insight.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomerInsightGeneratorView(APIView):
    permission_classes = [IsAdmin]
    
    def get(self, request):
        """Generate customer insights for all users"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Get all users
        users = User.objects.filter(user_type='CUSTOMER')
        
        for user in users:
            # Get all orders for this user
            user_orders = Order.objects.filter(user=user)
            
            if user_orders.exists():
                # Calculate metrics
                total_spent = user_orders.aggregate(Sum('total_price'))['total_price__sum'] or 0
                orders_count = user_orders.count()
                average_order_value = total_spent / orders_count if orders_count > 0 else 0
                
                # Get first and last purchase dates
                first_purchase = user_orders.order_by('created_at').first()
                last_purchase = user_orders.order_by('-created_at').first()
                
                first_purchase_date = first_purchase.created_at.date() if first_purchase else None
                last_purchase_date = last_purchase.created_at.date() if last_purchase else None
                
                # Find preferred category
                order_items = OrderItem.objects.filter(order__user=user)
                category_counts = {}
                
                for item in order_items:
                    category = item.product.category
                    if category in category_counts:
                        category_counts[category] += item.quantity
                    else:
                        category_counts[category] = item.quantity
                
                preferred_category = None
                max_count = 0
                
                for category, count in category_counts.items():
                    if count > max_count:
                        max_count = count
                        preferred_category = category
                
                # Create or update CustomerInsight
                insight, created = CustomerInsight.objects.update_or_create(
                    user=user,
                    defaults={
                        'total_spent': total_spent,
                        'orders_count': orders_count,
                        'average_order_value': average_order_value,
                        'first_purchase_date': first_purchase_date,
                        'last_purchase_date': last_purchase_date,
                        'preferred_category': preferred_category
                    }
                )
        
        # Return the generated data
        customer_insights = CustomerInsight.objects.all().order_by('-total_spent')
        serializer = CustomerInsightSerializer(customer_insights, many=True)
        return Response(serializer.data)


class SalesReportListView(APIView):
    permission_classes = [IsAdmin]
    
    def get(self, request):
        sales_reports = SalesReport.objects.all().order_by('-generated_at')
        serializer = SalesReportSerializer(sales_reports, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = SalesReportSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SalesReportDetailView(APIView):
    permission_classes = [IsAdmin]
    
    def get_object(self, pk):
        try:
            return SalesReport.objects.get(pk=pk)
        except SalesReport.DoesNotExist:
            return None
            
    def get(self, request, pk):
        sales_report = self.get_object(pk)
        if not sales_report:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = SalesReportSerializer(sales_report)
        return Response(serializer.data)
        
    def put(self, request, pk):
        sales_report = self.get_object(pk)
        if not sales_report:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = SalesReportSerializer(sales_report, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request, pk):
        sales_report = self.get_object(pk)
        if not sales_report:
            return Response(status=status.HTTP_404_NOT_FOUND)
        sales_report.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SalesReportGeneratorView(APIView):
    permission_classes = [IsAdmin]
    
    def post(self, request):
        """Generate a sales report for the given period"""
        report_type = request.data.get('report_type')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        
        if not report_type or not start_date or not end_date:
            return Response(
                {"error": "report_type, start_date, and end_date are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get orders in the date range
        orders = Order.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )
        
        if not orders.exists():
            return Response(
                {"error": "No orders found in the specified date range"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Calculate metrics
        total_sales = orders.aggregate(Sum('total_price'))['total_price__sum'] or 0
        total_orders = orders.count()
        average_order_value = total_sales / total_orders if total_orders > 0 else 0
        
        # Find top products
        top_products_data = OrderItem.objects.filter(
            order__in=orders
        ).values('product').annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum(F('quantity') * F('price'))
        ).order_by('-total_revenue')[:5]
        
        top_products = Product.objects.filter(id__in=[item['product'] for item in top_products_data])
        
        # Find top categories
        top_categories_data = OrderItem.objects.filter(
            order__in=orders
        ).values('product__category').annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum(F('quantity') * F('price'))
        ).order_by('-total_revenue')[:5]
        
        top_categories = Category.objects.filter(id__in=[item['product__category'] for item in top_categories_data])
        
        # Create a new SalesReport
        report = SalesReport.objects.create(
            report_type=report_type,
            start_date=start_date,
            end_date=end_date,
            total_sales=total_sales,
            total_orders=total_orders,
            average_order_value=average_order_value
        )
        
        # Add top products and categories
        report.top_products.set(top_products)
        report.top_categories.set(top_categories)
        
        serializer = SalesReportSerializer(report)
        return Response(serializer.data)
    
class UpdateSalesMetricsView(APIView):
    permission_classes = [IsAdmin]
    
    def post(self, request):
        from django.core.management import call_command
        call_command('update_sales_metrics')
        return Response({"message": "Sales metrics update triggered successfully"}, status=status.HTTP_200_OK)