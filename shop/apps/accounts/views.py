from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User
from .permissions import IsAdmin
from .serializers import UserSerializer
from .utils import send_verification_email, send_password_reset_email
import secrets
from django.utils import timezone
from datetime import timedelta


class SignupView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            verification_code = secrets.token_hex(3)

            user = serializer.save()
            user.verification_code = verification_code
            user.is_verified = False
            user.save()

            try:
                send_verification_email(user.email, verification_code)

                return Response({
                    'message': 'Registration sucessful. Please check your email for verification.',
                    'user': serializer.data
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                user.delete()
                return Response({
                    'message': 'Error sending verification email. Please try again later.',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class VerifyEmailView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        verification_code = request.data.get('verification_code')

        if not email or not verification_code:
            return Response({
                'message': 'Missing email or verification code.'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
            if user.verification_code != verification_code:
                return Response({
                    'message': 'Invalid verification code.'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            user.is_verified = True
            user.verification_code = None
            user.save()

            refresh = RefreshToken.for_user(user)
            serializer = UserSerializer(user)

            return Response({
                'message': 'Email verified successfully.',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': serializer.data
                }, status=status.HTTP_200_OK)
        
        except User.DoesNotExist:
            return Response({
                'message': 'Email not found.'
                }, status=status.HTTP_404_NOT_FOUND)
        
class ResendVerificationView(APIView):
    permission_classes = [permissions.AllowAny] 

    def post(self, request):
        email = request.data.get('email')
        
        try:
            user = User.objects.get(email=email)
            
            if user.is_verified:
                return Response({
                    'message': 'Email is already verified'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Generate new verification code
            verification_code = secrets.token_hex(3)
            user.verification_code = verification_code
            user.save()
            
            try:
                send_verification_email(email, verification_code)
                return Response({
                    'message': 'Verification code resent successfully'
                }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({
                    'message': 'Failed to send verification email'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except User.DoesNotExist:
            return Response({
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        

class RequestPasswordResetView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        
        try:
            user = User.objects.get(email=email)
            
            # Generate reset token
            reset_token = secrets.token_hex(3)
            user.password_reset_token = reset_token
            user.password_reset_token_created = timezone.now()
            user.save()
            
            try:
                send_password_reset_email(email, reset_token)
                return Response({
                    'message': 'Password reset instructions sent to your email'
                }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({
                    'message': 'Failed to send password reset email'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except User.DoesNotExist:
            # Return success even if email doesn't exist (security best practice)
            return Response({
                'message': 'If an account exists with this email, you will receive password reset instructions'
            }, status=status.HTTP_200_OK)
        
class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        token = request.data.get('token')
        new_password = request.data.get('new_password')
        
        if not all([email, token, new_password]):
            return Response({
                'message': 'Missing required fields'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            user = User.objects.get(email=email)
            
            # Check if token is valid and not expired (24 hour validity)
            if not user.password_reset_token or user.password_reset_token != token:
                return Response({
                    'message': 'Invalid reset token'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            token_age = timezone.now() - user.password_reset_token_created
            if token_age > timedelta(hours=24):
                return Response({
                    'message': 'Reset token has expired'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            # Reset password
            user.set_password(new_password)
            user.password_reset_token = None
            user.password_reset_token_created = None
            user.save()
            
            return Response({
                'message': 'Password reset successful'
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({
                'message': 'Invalid reset token'
            }, status=status.HTTP_400_BAD_REQUEST)
        

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(email=email, password=password)

        if user:
            # Skip verification check for admin users
            if not user.is_admin and not user.is_verified:
                return Response({
                    'detail': 'Email not verified.'
                    }, status=status.HTTP_403_FORBIDDEN)
            
            refresh = RefreshToken.for_user(user)
            serializer = UserSerializer(user)

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': serializer.data
            })
        
        return Response({
            'detail': 'Invalid email or password.'
            }, status=status.HTTP_401_UNAUTHORIZED)
    

class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserListView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdmin]  # Only admins can access

    def get(self, request):
        """Fetch all users (admin-only)"""
        users = User.objects.all()  # Retrieve all users
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
