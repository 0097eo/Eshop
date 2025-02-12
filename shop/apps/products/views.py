from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Category, Product, ProductReview, WishList
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    ProductReviewSerializer,
    WishListSerializer,
    ProductPagination
)
from ..accounts.permissions import IsAdmin, IsCustomer
from rest_framework.parsers import MultiPartParser, FormParser



# Category Views
class CategoryListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdmin()]
        return [permissions.AllowAny()]

    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CategoryDetailView(APIView):
    def get_permissions(self):
        if self.request.method in ['PUT', 'DELETE']:
            return [IsAdmin()]
        return [permissions.AllowAny()]

    def get_object(self, pk):
        return get_object_or_404(Category, pk=pk)

    def get(self, request, pk):
        category = self.get_object(pk)
        serializer = CategorySerializer(category)
        return Response(serializer.data)

    def put(self, request, pk):
        category = self.get_object(pk)
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        category = self.get_object(pk)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Product Views
class ProductListCreateView(APIView):
    pagination_class = ProductPagination
    parser_classes = (MultiPartParser, FormParser)

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdmin()]
        return [permissions.AllowAny()]

    def get(self, request):
        queryset = Product.objects.all()

        # Search functionality
        search_query = request.query_params.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(category__name__icontains=search_query) |
                Q(primary_material__icontains=search_query)
            )

        # Filters
        category = request.query_params.get('category')
        if category:
            queryset = queryset.filter(category_id=category)

        material = request.query_params.get('material')
        if material:
            queryset = queryset.filter(primary_material=material)

        condition = request.query_params.get('condition')
        if condition:
            queryset = queryset.filter(condition=condition)

        min_price = request.query_params.get('min_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)

        max_price = request.query_params.get('max_price')
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        is_available = request.query_params.get('available')
        if is_available is not None:
            queryset = queryset.filter(is_available=is_available.lower() == 'true')

        # Ordering
        ordering = request.query_params.get('ordering', '-created_at')
        valid_orderings = ['price', '-price', 'created_at', '-created_at', 'name', '-name']
        if ordering in valid_orderings:
            queryset = queryset.order_by(ordering)

        # Pagination
        paginator = self.pagination_class()
        paginated_products = paginator.paginate_queryset(queryset, request)
        serializer = ProductSerializer(paginated_products, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductDetailView(APIView):
    def get_permissions(self):
        if self.request.method in ['PUT', 'DELETE']:
            return [IsAdmin()]
        return [permissions.AllowAny()]

    def get_object(self, pk):
        return get_object_or_404(Product, pk=pk)

    def get(self, request, pk):
        product = self.get_object(pk)
        serializer = ProductSerializer(product, context={'request': request})
        return Response(serializer.data)

    def put(self, request, pk):
        product = self.get_object(pk)
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        product = self.get_object(pk)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Product Review Views
class ProductReviewListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, product_pk):
        reviews = ProductReview.objects.filter(product_id=product_pk)
        serializer = ProductReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    def post(self, request, product_pk):
        product = get_object_or_404(Product, pk=product_pk)
        
        # Check if user has already reviewed this product
        if ProductReview.objects.filter(product=product, user=request.user).exists():
            return Response(
                {'message': 'You have already reviewed this product'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ProductReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductReviewDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, product_pk, review_pk):
        return get_object_or_404(ProductReview, product_id=product_pk, pk=review_pk)

    def get(self, request, product_pk, review_pk):
        review = self.get_object(product_pk, review_pk)
        serializer = ProductReviewSerializer(review)
        return Response(serializer.data)

    def put(self, request, product_pk, review_pk):
        review = self.get_object(product_pk, review_pk)
        if review.user != request.user and not request.user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)
            
        serializer = ProductReviewSerializer(review, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, product_pk, review_pk):
        review = self.get_object(product_pk, review_pk)
        if review.user != request.user and not request.user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)
            
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Wishlist Views
class WishListView(APIView):
    permission_classes = [IsCustomer]

    def get(self, request):
        wishlist, _ = WishList.objects.get_or_create(user=request.user)
        serializer = WishListSerializer(wishlist)
        return Response(serializer.data)

    def post(self, request):
        product_id = request.data.get('product_id')
        if not product_id:
            return Response(
                {'message': 'Product ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            product = Product.objects.get(id=product_id)
            wishlist, _ = WishList.objects.get_or_create(user=request.user)

            if product in wishlist.products.all():
                return Response(
                    {'message': 'Product already in wishlist'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            wishlist.products.add(product)
            serializer = WishListSerializer(wishlist)
            return Response(serializer.data)

        except Product.DoesNotExist:
            return Response(
                {'message': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )

class WishListItemView(APIView):
    permission_classes = [IsCustomer]

    def delete(self, request, product_id):
        try:
            wishlist = WishList.objects.get(user=request.user)
            product = Product.objects.get(id=product_id)

            if product not in wishlist.products.all():
                return Response(
                    {'message': 'Product not in wishlist'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            wishlist.products.remove(product)
            return Response(status=status.HTTP_204_NO_CONTENT)

        except (WishList.DoesNotExist, Product.DoesNotExist):
            return Response(
                {'message': 'Product or wishlist not found'},
                status=status.HTTP_404_NOT_FOUND
            )