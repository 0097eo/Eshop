from django.conf import settings
from django.core.mail import send_mail


def send_verification_email(email, verification_code):
    subject = 'Verify your email address'
    body  = f'Your verification code is: {verification_code}'
    
    try:
        send_mail(
            subject,
            body,
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )
    except Exception as e:
        print(f'Error sending verification email: {e}')

def send_password_reset_email(email, reset_token):
    subject = "E-commerce: Password Reset Request"
    body = f"Your password reset code is: {reset_token}\n\nIf you didn't request this, please ignore this email."
    
    try:
        send_mail(
            subject,
            body,
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )
    
    except Exception as e:
        print(f'Error sending password reset email: {e}')