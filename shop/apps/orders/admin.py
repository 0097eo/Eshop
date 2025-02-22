from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ('product', 'quantity', 'price', 'get_subtotal')

    def get_subtotal(self, obj):
        return obj.get_subtotal()
    get_subtotal.short_description = 'Subtotal'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_price', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__email', 'id', 'status')
    readonly_fields = ('total_price', 'created_at', 'updated_at')
    inlines = [OrderItemInline]

    fieldsets = (
        ('Order Information', {
            'fields': ('user', 'status', 'total_price', 'created_at', 'updated_at')
        }),
        ('Addresses', {
            'fields': ('shipping_address', 'billing_address')
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.total_price:
            obj.total_price = obj.get_total_price()
        super().save_model(request, obj, form, change)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'price', 'get_subtotal', 'created_at')
    list_filter = ('order__status', 'created_at')
    search_fields = ('order__id', 'product__name')
    readonly_fields = ('get_subtotal',)

    def get_subtotal(self, obj):
        return (obj.price or 0) * (obj.quantity or 0)
    get_subtotal.short_description = 'Subtotal'

    def save_model(self, request, obj, form, change):
        if obj.price is None and obj.product:
            obj.price = obj.product.price  # Set price from the product
        super().save_model(request, obj, form, change)
