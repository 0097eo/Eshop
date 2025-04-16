from . import views
from django.urls import path
from django.contrib import admin
from django.core.management import call_command


def create_superuser(request):
    call_command('create_superuser')
    from django.http import HttpResponse
    return HttpResponse("Superuser created successfully!")

urlpatterns = [
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('verify-email/', views.VerifyEmailView.as_view(), name='verify-email'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
     path('resend-verification/', views.ResendVerificationView.as_view(), name='resend-verification'),
    path('request-password-reset/', views.RequestPasswordResetView.as_view(), name='request-password-reset'),
    path('reset-password/', views.ResetPasswordView.as_view(), name='reset-password'),
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('admin/', admin.site.urls),
    path('create-superuser/', create_superuser),
]