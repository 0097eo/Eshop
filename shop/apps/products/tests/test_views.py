from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from ..models import Category, Product, ProductReview, WishList
from django.contrib.auth import get_user_model


User = get_user_model()

class CategoryViewsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            email='admin@test.com', 
            password='testpass123',
            is_staff=True
        )
        self.normal_user = User.objects.create_user(
            email='user@test.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Test Category')
        
    def test_category_list(self):
        response = self.client.get(reverse('category-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_category_create_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'name': 'New Category'}
        response = self.client.post(reverse('category-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_category_create_as_normal_user(self):
        self.client.force_authenticate(user=self.normal_user)
        data = {'name': 'New Category'}
        response = self.client.post(reverse('category-list'), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class ProductViewsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            email='admin@test.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            name='Test Product',
            description='Test Description',
            price=99.99,
            category=self.category,
            primary_material='Wood',
            condition='New',
            is_available=True
        )

    def test_product_list(self):
        response = self.client.get(reverse('product-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_product_search(self):
        response = self.client.get(f"{reverse('product-list')}?search=Test")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_product_filters(self):
        response = self.client.get(
            f"{reverse('product-list')}?category={self.category.id}&material=Wood"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_product_create_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'name': 'New Product',
            'description': 'New Description',
            'price': 149.99,
            'category': self.category.id,
            'primary_material': 'METAL',
            'condition': 'NEW',
            'is_available': True
        }
        response = self.client.post(reverse('product-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

class ProductReviewViewsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='user@test.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            name='Test Product',
            description='Test Description',
            price=99.99,
            category=self.category
        )
        self.review = ProductReview.objects.create(
            user=self.user,
            product=self.product,
            rating=5,
            comment='Great product!'
        )

    def test_review_list(self):
        response = self.client.get(
            reverse('product-review-list', kwargs={'product_pk': self.product.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_review_authenticated(self):
        self.client.force_authenticate(user=self.user)
        product = Product.objects.create(
            name='Another Product',
            description='Another Description',
            price=149.99,
            category=self.category
        )
        data = {
            'rating': 4,
            'comment': 'Good product'
        }
        response = self.client.post(
            reverse('product-review-list', kwargs={'product_pk': product.pk}),
            data
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

class WishListViewsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='user@test.com',
            password='testpass123',
        )
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            name='Test Product',
            description='Test Description',
            price=99.99,
            category=self.category
        )

    def test_wishlist_get(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('wishlist'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_add_to_wishlist(self):
        self.client.force_authenticate(user=self.user)
        data = {'product_id': self.product.id}
        response = self.client.post(reverse('wishlist'), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_remove_from_wishlist(self):
        self.client.force_authenticate(user=self.user)
        wishlist = WishList.objects.create(user=self.user)
        wishlist.products.add(self.product)
        
        response = self.client.delete(
            reverse('wishlist-item', kwargs={'product_id': self.product.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)