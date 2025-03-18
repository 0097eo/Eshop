from django.core.management.base import BaseCommand
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta
from ...models import DailySales, ProductPerformance, CategoryPerformance, CustomerInsight
from ....orders.models import Order, OrderItem
from ....products.models import Product, Category
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Updates all sales metrics'

    def handle(self, *args, **options):
        self.stdout.write('Updating sales metrics...')
        
        # Get date range (last 30 days as an example)
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)

        # Update Daily Sales
        self.update_daily_sales(start_date, end_date)
        
        # Update Product Performance
        self.update_product_performance(start_date, end_date)
        
        # Update Category Performance
        self.update_category_performance(start_date, end_date)
        
        # Update Customer Insights
        self.update_customer_insights()
        
        self.stdout.write(self.style.SUCCESS('Successfully updated all sales metrics'))

    def update_daily_sales(self, start_date, end_date):
        orders = Order.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )
        
        delta = end_date - start_date
        for i in range(delta.days + 1):
            current_date = start_date + timedelta(days=i)
            daily_orders = orders.filter(created_at__date=current_date)
            
            if daily_orders.exists():
                total_sales = daily_orders.aggregate(Sum('total_price'))['total_price__sum'] or 0
                order_count = daily_orders.count()
                unique_customers = daily_orders.values('user').distinct().count()
                
                new_customers = sum(1 for order in daily_orders if not Order.objects.filter(
                    user=order.user,
                    created_at__date__lt=current_date
                ).exists())
                
                DailySales.objects.update_or_create(
                    date=current_date,
                    defaults={
                        'total_sales': total_sales,
                        'order_count': order_count,
                        'average_order_value': total_sales/order_count if order_count > 0 else 0,
                        'unique_customers': unique_customers,
                        'new_customers': new_customers
                    }
                )

    def update_product_performance(self, start_date, end_date):
        order_items = OrderItem.objects.filter(
            order__created_at__date__gte=start_date,
            order__created_at__date__lte=end_date
        )
        
        products = Product.objects.all()
        delta = end_date - start_date
        
        for i in range(delta.days + 1):
            current_date = start_date + timedelta(days=i)
            for product in products:
                product_items = order_items.filter(
                    product=product,
                    order__created_at__date=current_date
                )
                
                if product_items.exists():
                    units_sold = product_items.aggregate(Sum('quantity'))['quantity__sum'] or 0
                    revenue = sum(item.quantity * item.price for item in product_items)
                    avg_rating = product.reviews.aggregate(Avg('rating'))['rating__avg']
                    
                    ProductPerformance.objects.update_or_create(
                        date=current_date,
                        product=product,
                        defaults={
                            'units_sold': units_sold,
                            'revenue': revenue,
                            'average_rating': avg_rating
                        }
                    )

    def update_category_performance(self, start_date, end_date):
        order_items = OrderItem.objects.filter(
            order__created_at__date__gte=start_date,
            order__created_at__date__lte=end_date
        )
        
        categories = Category.objects.all()
        delta = end_date - start_date
        
        for i in range(delta.days + 1):
            current_date = start_date + timedelta(days=i)
            for category in categories:
                category_items = order_items.filter(
                    product__category=category,
                    order__created_at__date=current_date
                )
                
                if category_items.exists():
                    products_sold = category_items.aggregate(Sum('quantity'))['quantity__sum'] or 0
                    revenue = sum(item.quantity * item.price for item in category_items)
                    
                    CategoryPerformance.objects.update_or_create(
                        date=current_date,
                        category=category,
                        defaults={
                            'products_sold': products_sold,
                            'revenue': revenue
                        }
                    )

    def update_customer_insights(self):
        users = User.objects.filter(user_type='CUSTOMER')
        
        for user in users:
            user_orders = Order.objects.filter(user=user)
            if user_orders.exists():
                total_spent = user_orders.aggregate(Sum('total_price'))['total_price__sum'] or 0
                orders_count = user_orders.count()
                
                first_purchase = user_orders.order_by('created_at').first()
                last_purchase = user_orders.order_by('-created_at').first()
                
                # Calculate preferred category
                order_items = OrderItem.objects.filter(order__user=user)
                category_counts = {}
                for item in order_items:
                    cat = item.product.category
                    category_counts[cat] = category_counts.get(cat, 0) + item.quantity
                
                preferred_category = max(category_counts.items(), key=lambda x: x[1])[0] if category_counts else None
                
                CustomerInsight.objects.update_or_create(
                    user=user,
                    defaults={
                        'total_spent': total_spent,
                        'orders_count': orders_count,
                        'average_order_value': total_spent/orders_count if orders_count > 0 else 0,
                        'first_purchase_date': first_purchase.created_at.date() if first_purchase else None,
                        'last_purchase_date': last_purchase.created_at.date() if last_purchase else None,
                        'preferred_category': preferred_category
                    }
                )