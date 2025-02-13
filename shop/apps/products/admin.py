from django.contrib import admin
from .models import Category, Product, ProductReview, WishList

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    list_filter = ('name', 'description')
    search_fields = ('name', 'description')
    ordering = ('name',)


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'description', 'price', 'stock', 'primary_material', 'condition', 'is_available', 'created_at', 'updated_at')
    list_filter = ('name', 'category', 'primary_material', 'condition', 'is_available', 'created_at')
    search_fields = ('name', 'description', 'category')
    ordering = ('name',)
    

class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'comment')
    list_filter = ('product', 'user', 'rating',)
    search_fields = ('product__name', 'user__email', 'comment')
    ordering = ('created_at',)

class WishListAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    list_filter = ('user',)
    ordering = ('created_at',)
    search_fields = ('user__email',)
    filter_horizontal = ('products',) # for better many to many field management



admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductReview, ProductReviewAdmin)
admin.site.register(WishList, WishListAdmin)