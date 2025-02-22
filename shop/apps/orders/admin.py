from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    fields = ('product', 'quantity', 'price', 'get_subtotal')
    readonly_fields = ('get_subtotal',)
    
    def get_subtotal(self, obj):
        if obj.price and obj.quantity:
            return obj.price * obj.quantity
        return 0
    get_subtotal.short_description = 'Subtotal'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'user_email', 
        'status', 
        'total_price', 
        'items_count',
        'created_at', 
        'updated_at',
        'view_order_items'
    )
    list_filter = (
        'status', 
        'created_at', 
        'updated_at',
        ('user', admin.RelatedOnlyFieldListFilter),
    )
    search_fields = (
        'user__email', 
        'id', 
        'shipping_address', 
        'billing_address'
    )
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'user',
                'status',
                'total_price',
            )
        }),
        ('Addresses', {
            'fields': (
                'shipping_address',
                'billing_address',
            ),
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',),
        }),
    )
    
    actions = ['mark_as_processing', 'mark_as_shipped', 'mark_as_delivered', 'mark_as_cancelled']
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return ('created_at', 'updated_at')
        return ('created_at', 'updated_at', 'total_price')
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Customer Email'
    user_email.admin_order_field = 'user__email'
    
    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = 'Number of Items'
    
    def view_order_items(self, obj):
        if obj.id:  # Ensure order has been saved before generating the link
            url = reverse('admin:orders_orderitem_changelist')
            return format_html('<a href="{}?order__id__exact={}">View Items</a>', url, obj.id)
        return "No items yet"
    view_order_items.short_description = 'Order Items'
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.total_price = 0  # Initialize price before first save
        super().save_model(request, obj, form, change)
    
    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        if form.instance.pk:  # Ensure order has been saved before accessing related fields
            form.instance.total_price = form.instance.get_total_price()
            form.instance.save()
    
    def mark_as_processing(self, request, queryset):
        updated = queryset.update(status='PROCESSING', updated_at=timezone.now())
        self._send_status_update_message(request, updated, "processing")
    mark_as_processing.short_description = "Mark selected orders as processing"
    
    def mark_as_shipped(self, request, queryset):
        updated = queryset.update(status='SHIPPED', updated_at=timezone.now())
        self._send_status_update_message(request, updated, "shipped")
    mark_as_shipped.short_description = "Mark selected orders as shipped"
    
    def mark_as_delivered(self, request, queryset):
        updated = queryset.update(status='DELIVERED', updated_at=timezone.now())
        self._send_status_update_message(request, updated, "delivered")
    mark_as_delivered.short_description = "Mark selected orders as delivered"
    
    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status='CANCELLED', updated_at=timezone.now())
        self._send_status_update_message(request, updated, "cancelled")
    mark_as_cancelled.short_description = "Mark selected orders as cancelled"
    
    def _send_status_update_message(self, request, updated, status):
        messages.success(request, f'{updated} orders were successfully marked as {status}.')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'order_link',
        'product_link',
        'quantity',
        'price',
        'get_subtotal',
        'created_at'
    )
    list_filter = (
        'created_at',
        ('order', admin.RelatedOnlyFieldListFilter),
        ('product', admin.RelatedOnlyFieldListFilter),
    )
    search_fields = (
        'order__id',
        'product__name',
        'product__sku'
    )
    ordering = ('-created_at',)
    
    fields = (
        'order',
        'product',
        'quantity',
        'price',
        'created_at'
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return ('created_at', 'order')
        return ('created_at',)
    
    def order_link(self, obj):
        if obj.order.id:  # Ensure order exists before linking
            url = reverse('admin:orders_order_change', args=[obj.order.id])
            return format_html('<a href="{}">{}</a>', url, f'Order #{obj.order.id}')
        return "No Order"
    order_link.short_description = 'Order'
    order_link.admin_order_field = 'order'
    
    def product_link(self, obj):
        if obj.product.id:  # Ensure product exists before linking
            url = reverse('admin:products_product_change', args=[obj.product.id])
            return format_html('<a href="{}">{}</a>', url, obj.product.name)
        return "No Product"
    product_link.short_description = 'Product'
    product_link.admin_order_field = 'product__name'
    
    def get_subtotal(self, obj):
        return obj.get_subtotal()
    get_subtotal.short_description = 'Subtotal'
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.order and obj.order.pk:  # Ensure order is saved before updating total
            obj.order.total_price = obj.order.get_total_price() or 0
            obj.order.save()

    
