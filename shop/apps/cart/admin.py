from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum
from .models import Cart, CartItem

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('total_price',)
    fields = ('product', 'quantity', 'total_price')

    def total_price(self, obj):
        if obj.product and obj.quantity:
            return f"${obj.product.price * obj.quantity:.2f}"
        return "$0.00"
    total_price.short_description = 'Total Price'

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'items_count', 'total_value', 'created_at', 'updated_at', 'cart_status')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    inlines = [CartItemInline]
    readonly_fields = ('created_at', 'updated_at', 'total_value')
    date_hierarchy = 'created_at'

    fieldsets = (
        (None, {
            'fields': ('user',)
        }),
        ('Cart Information', {
            'fields': ('created_at', 'updated_at', 'total_value')
        }),
    )

    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = 'Number of Items'

    def total_value(self, obj):
        total = sum(item.quantity * item.product.price for item in obj.items.all())
        return f"${total:.2f}"
    total_value.short_description = 'Total Value'

    def cart_status(self, obj):
        if not obj.items.exists():
            return format_html('<span style="color: red;">Empty</span>')
        return format_html('<span style="color: green;">Has Items</span>')
    cart_status.short_description = 'Status'

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart_user', 'product', 'quantity', 'item_total', 'added_at')
    list_filter = ('cart__created_at', 'cart__user')
    search_fields = ('cart__user__email', 'product__name')
    readonly_fields = ('added_at',)

    fieldsets = (
        (None, {
            'fields': ('cart', 'product', 'quantity')
        }),
        ('Timing Information', {
            'fields': ('added_at',)
        }),
    )

    def cart_user(self, obj):
        return obj.cart.user
    cart_user.short_description = 'User'

    def item_total(self, obj):
        return f"${obj.product.price * obj.quantity:.2f}"
    item_total.short_description = 'Total Price'

    def added_at(self, obj):
        return obj.cart.created_at
    added_at.short_description = 'Added At'