from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

class UserModelTest(TestCase):

    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpassword'
        }
        self.User = get_user_model()

    def test_create_user(self):
        user = self.User.objects.create_user(**self.user_data)
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpassword'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        user = self.User.objects.create_superuser(
            email=self.user_data['email'],
            password=self.user_data['password'],
            first_name=self.user_data['first_name'],
            last_name=self.user_data['last_name']
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpassword'))
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_admin)
        self.assertEqual(user.user_type, 'ADMIN')

    def test_create_user_no_email(self):
        with self.assertRaises(ValueError) as context:
            self.User.objects.create_user(email=None, first_name='Test', last_name='User')
        self.assertEqual(str(context.exception), 'Email is required')

    def test_user_str_representation(self):
        user = self.User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), 'test@example.com')

    