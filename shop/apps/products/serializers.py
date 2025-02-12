from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from django.db.models import Avg
from .models import Category, Product, ProductReview, WishList


class ProductPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'description')

    
class ProductReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = ProductReview
        fields = ['id', 'user', 'rating', 'comment', 'created_at']
        
    def validate(self, data):
        if 'rating' in data and not (1 <= data['rating'] <= 5):
            raise serializers.ValidationError({"rating": "Rating must be between 1 and 5"})
        return data
    

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    reviews = ProductReviewSerializer(many=True, read_only=True)
    image = serializers.ImageField(required=False)
    
    class Meta:
        model = Product
        fields = [
            'id', 'category', 'category_name', 'name', 'description',
            'price', 'stock', 'primary_material', 'condition',
            'image', 'additional_images', 'is_available', 'created_at',
            'average_rating', 'review_count', 'reviews'
        ]
        read_only_fields = ['created_at']

    def get_average_rating(self, obj):
        avg = obj.reviews.aggregate(Avg('rating'))['rating__avg']
        return round(avg, 2) if avg else None

    def get_review_count(self, obj):
        return obj.reviews.count()

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero")
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative")
        return value
    

class WishListSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    
    class Meta:
        model = WishList
        fields = ['id', 'products', 'created_at']
        read_only_fields = ['created_at']