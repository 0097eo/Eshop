from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from ..models import User
from unittest.mock import patch

class BaseTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'email': 'test@example.com',
            'password': 'testpassword',
            'first_name': 'Test',
            'last_name': 'User'
        }

    def create_user(self, email='test@example.com', password='testpassword'):
        return User.objects.create_user(email=email, password=password)

class SignupViewTests(BaseTestCase):
    @patch('apps.accounts.utils.send_verification_email')
    def test_signup_success(self, mock_send_email):
        mock_send_email.return_value = None
        response = self.client.post(reverse('signup'), self.user_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='test@example.com').exists())
        self.assertIn('message', response.data)
        self.assertIn('user', response.data)
        

    def test_signup_failure(self):
        data = {'email': 'invalid-email', 'password': 'testpassword'}
        response = self.client.post(reverse('signup'), data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

class VerifyEmailViewTests(BaseTestCase):
    def test_verify_email_success(self):
        user = self.create_user()
        user.verification_code = '123456'
        user.save()

        data = {'email': user.email, 'verification_code': '123456'}
        response = self.client.post(reverse('verify-email'), data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.is_verified)
        self.assertIsNone(user.verification_code)
        self.assertIn('message', response.data)

    def test_verify_email_missing_data(self):
        response = self.client.post(reverse('verify-email'), {})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('message', response.data)

    def test_verify_email_invalid_code(self):
        user = self.create_user()
        user.verification_code = '123456'
        user.save()

        data = {'email': user.email, 'verification_code': 'wrongcode'}
        response = self.client.post(reverse('verify-email'), data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('message', response.data)

class ResendVerificationViewTests(BaseTestCase):
    @patch('apps.accounts.utils.send_verification_email')
    def test_resend_verification_success(self, mock_send_email):
        user = self.create_user()
        
        response = self.client.post(reverse('resend-verification'), {'email': user.email})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        user.refresh_from_db()
        self.assertIsNotNone(user.verification_code)
        

    def test_resend_verification_already_verified(self):
        user = self.create_user()
        user.is_verified = True
        user.save()

        response = self.client.post(reverse('resend-verification'), {'email': user.email})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('message', response.data)

class RequestPasswordResetViewTests(BaseTestCase):
    @patch('apps.accounts.utils.send_password_reset_email')
    def test_request_password_reset_success(self, mock_send_email):
        mock_send_email.return_value = None
        user = self.create_user()
        
        response = self.client.post(reverse('request-password-reset'), {'email': user.email})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        user.refresh_from_db()
        self.assertIsNotNone(user.password_reset_token)
        

    def test_request_password_reset_user_not_found(self):
        response = self.client.post(reverse('request-password-reset'), 
                                  {'email': 'nonexistent@example.com'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)

class ResetPasswordViewTests(BaseTestCase):
    def test_reset_password_success(self):
        user = self.create_user()
        user.password_reset_token = 'resettoken'
        user.password_reset_token_created = timezone.now()
        user.save()

        data = {
            'email': user.email,
            'token': 'resettoken',
            'new_password': 'newpassword'
        }
        response = self.client.post(reverse('reset-password'), data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        user.refresh_from_db()
        self.assertIsNone(user.password_reset_token)
        self.assertIsNone(user.password_reset_token_created)
        self.assertTrue(user.check_password('newpassword'))

class LoginViewTests(BaseTestCase):
    def test_login_success(self):
        user = self.create_user()
        user.is_verified = True
        user.save()

        data = {'email': user.email, 'password': 'testpassword'}
        response = self.client.post(reverse('login'), data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)
        self.assertIn('user', response.data)

    def test_login_unverified_email(self):
        user = self.create_user()
        
        data = {'email': user.email, 'password': 'testpassword'}
        response = self.client.post(reverse('login'), data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('detail', response.data)

class ProfileViewTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.user = self.create_user()
        self.client.force_authenticate(user=self.user)

    def test_get_profile(self):
        response = self.client.get(reverse('profile'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('email', response.data)
        self.assertEqual(response.data['email'], self.user.email)

    def test_update_profile(self):
        response = self.client.put(
            reverse('profile'),
            {'first_name': 'Updated'},
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')