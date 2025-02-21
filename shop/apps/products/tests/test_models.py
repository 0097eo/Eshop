from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from decimal import Decimal
from ..models import Category, Product, ProductReview, WishList

User = get_user_model()

class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Chairs',
            description='Comfortable chairs'
        )

    def test_category_creation(self):
        self.assertEqual(self.category.name, 'Chairs')
        self.assertEqual(self.category.description, 'Comfortable chairs')
        self.assertTrue(self.category.created_at)
        self.assertTrue(self.category.updated_at)

    def test_category_str_method(self):
        self.assertEqual(str(self.category), 'Chairs')

class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Chairs')
        self.product = Product.objects.create(
            category=self.category,
            name='Office Chair',
            description='Ergonomic office chair',
            price=Decimal('199.99'),
            stock=10,
            primary_material='FABRIC',
            condition='NEW',
            image='test_image.jpg'
        )

    def test_product_creation(self):
        self.assertEqual(self.product.name, 'Office Chair')
        self.assertEqual(self.product.price, Decimal('199.99'))
        self.assertEqual(self.product.stock, 10)
        self.assertEqual(self.product.primary_material, 'FABRIC')
        self.assertEqual(self.product.condition, 'NEW')
        self.assertTrue(self.product.is_available)

    def test_product_str_method(self):
        self.assertEqual(str(self.product), 'Office Chair')

class ProductReviewModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Chairs')
        self.product = Product.objects.create(
            category=self.category,
            name='Office Chair',
            price=Decimal('199.99'),
            primary_material='FABRIC',
            condition='NEW',
            image='test_image.jpg'
        )
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.review = ProductReview.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            comment='Great product!'
        )

    def test_review_creation(self):
        self.assertEqual(self.review.rating, 5)
        self.assertEqual(self.review.comment, 'Great product!')
        self.assertEqual(self.review.user, self.user)
        self.assertEqual(self.review.product, self.product)

    def test_review_unique_constraint(self):
        with self.assertRaises(IntegrityError):
            ProductReview.objects.create(
                product=self.product,
                user=self.user,
                rating=4,
                comment='Another review'
            )

    def test_review_str_method(self):
        expected_str = f'Review by {self.user} on {self.product}'
        self.assertEqual(str(self.review), expected_str)

class WishListModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Chairs')
        self.product = Product.objects.create(
            category=self.category,
            name='Office Chair',
            price=Decimal('199.99'),
            primary_material='FABRIC',
            condition='NEW',
            image='test_image.jpg'
        )
        self.wishlist = WishList.objects.create(user=self.user)
        self.wishlist.products.add(self.product)

    def test_wishlist_creation(self):
        self.assertEqual(self.wishlist.user, self.user)
        self.assertEqual(self.wishlist.products.count(), 1)
        self.assertIn(self.product, self.wishlist.products.all())

    def test_wishlist_str_method(self):
        self.assertEqual(str(self.wishlist), f'Wishlist for {self.user}')