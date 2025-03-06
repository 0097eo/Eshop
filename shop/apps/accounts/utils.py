from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_verification_email(email, verification_code):
    subject = 'Verify your email address'
    
    # HTML version of the email
    html_message = render_to_string('emails/verification_email.html', {
        'verification_code': verification_code,
        'company_name': 'Eshop',
        'support_email': 'support@eshop.com',
    })
    
    # Plain text version of the email
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject,
            plain_message,
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
            html_message=html_message,
        )
    except Exception as e:
        print(f'Error sending verification email: {e}')


def send_password_reset_email(email, reset_token):
    subject = "Eshop: Password Reset Request"
    
    # HTML version of the email
    html_message = render_to_string('emails/password_reset_email.html', {
        'reset_token': reset_token,
        'company_name': 'Eshop',
        'support_email': 'support@eshop.com',
    })
    
    # Plain text version of the email
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject,
            plain_message,
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
            html_message=html_message,
        )
    except Exception as e:
        print(f'Error sending password reset email: {e}')
