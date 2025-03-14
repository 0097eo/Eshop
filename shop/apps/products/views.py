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
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
import cloudinary
import cloudinary.uploader
from django.conf import settings
import csv
import json
import requests
from io import TextIOWrapper
from django.db import transaction



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

# Bulk Product import from CSV or JSON format
class BulkProductImportView(APIView):
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    permission_classes = [IsAdmin]

    def _upload_to_cloudinary(self, image_url):
        """Upload image to Cloudinary either from URL or file"""
        try:
            if isinstance(image_url, str):
                upload_result = cloudinary.uploader.upload(
                    image_url,
                    folder="products/", 
                    use_filename=True,    
                    unique_filename=True, 
                    overwrite=False,     
                    resource_type="auto"  
                )
                return upload_result.get('secure_url')
            else:
                # Handle file upload if image_url is actually a file
                upload_result = cloudinary.uploader.upload(
                    image_url,
                    folder="products/",
                    use_filename=True,
                    unique_filename=True,
                    overwrite=False,
                    resource_type="auto"
                )
                return upload_result.get('secure_url')
        except Exception as e:
            raise ValueError(f"Cloudinary upload failed: {str(e)}")

    def _validate_image_url(self, url):
        """Validate if the URL points to an image"""
        try:
            response = requests.head(url, timeout=5)
            content_type = response.headers.get('content-type', '')
            return content_type.startswith('image/')
        except:
            return False

    def _process_csv(self, file):
        results = {
            'successful': 0,
            'failed': 0,
            'errors': []
        }

        csv_file = TextIOWrapper(file, encoding='utf-8')
        reader = csv.DictReader(csv_file)
        
        with transaction.atomic():
            for row_number, row in enumerate(reader, start=2):
                try:
                    category = None
                    if 'category' in row:
                        category, _ = Category.objects.get_or_create(name=row['category'])

                    image_url = None
                    if 'image_url' in row and row['image_url']:
                        if self._validate_image_url(row['image_url']):
                            image_url = self._upload_to_cloudinary(row['image_url'])
                        else:
                            results['errors'].append(f"Row {row_number}: Invalid image URL")

                    product_data = {
                        'name': row['name'],
                        'description': row['description'],
                        'price': float(row['price']),
                        'category': category.id if category else None,
                        'primary_material': row.get('primary_material', ''),
                        'condition': row.get('condition', ''),
                        'is_available': row.get('is_available', 'true').lower() == 'true'
                    }

                    if image_url:
                        product_data['image'] = image_url

                    serializer = ProductSerializer(data=product_data)
                    if serializer.is_valid():
                        serializer.save()
                        results['successful'] += 1
                    else:
                        results['failed'] += 1
                        results['errors'].append(f"Row {row_number}: {serializer.errors}")

                except Exception as e:
                    results['failed'] += 1
                    results['errors'].append(f"Row {row_number}: {str(e)}")

        return results

    def _process_json(self, file):
        results = {
            'successful': 0,
            'failed': 0,
            'errors': []
        }

        try:
            products_data = json.load(file)
            
            with transaction.atomic():
                for index, product_data in enumerate(products_data, start=1):
                    try:
                        if 'category' in product_data:
                            category, _ = Category.objects.get_or_create(
                                name=product_data['category']
                            )
                            product_data['category'] = category.id

                        if 'image_url' in product_data and product_data['image_url']:
                            if self._validate_image_url(product_data['image_url']):
                                image_url = self._upload_to_cloudinary(product_data['image_url'])
                                if image_url:
                                    product_data['image'] = image_url
                            else:
                                results['errors'].append(f"Product {index}: Invalid image URL")
                            
                            # Remove image_url from data as it's not part of the model
                            del product_data['image_url']

                        serializer = ProductSerializer(data=product_data)
                        if serializer.is_valid():
                            serializer.save()
                            results['successful'] += 1
                        else:
                            results['failed'] += 1
                            results['errors'].append(f"Product {index}: {serializer.errors}")

                    except Exception as e:
                        results['failed'] += 1
                        results['errors'].append(f"Product {index}: {str(e)}")

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {str(e)}")

        return results

    def post(self, request):
        if not all([
            settings.CLOUDINARY_STORAGE.get('CLOUD_NAME'),
            settings.CLOUDINARY_STORAGE.get('API_KEY'),
            settings.CLOUDINARY_STORAGE.get('API_SECRET')
        ]):
            return Response(
                {'error': 'Cloudinary configuration is incomplete'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        file = request.FILES.get('file')
        if not file:
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Determine file type from extension
        file_name = file.name.lower()
        results = {
            'successful': 0,
            'failed': 0,
            'errors': []
        }

        try:
            if file_name.endswith('.csv'):
                results = self._process_csv(file)
            elif file_name.endswith('.json'):
                results = self._process_json(file)
            else:
                return Response(
                    {'error': 'Unsupported file format. Please use CSV or JSON'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response({
                'message': 'Import completed',
                'results': results
            }, status=status.HTTP_201_CREATED if results['successful'] > 0 else status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


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
    
class UserReviewsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Get all reviews by the current user
        reviews = ProductReview.objects.filter(user=request.user)
        serializer = ProductReviewSerializer(reviews, many=True)
        return Response(serializer.data)

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