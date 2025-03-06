from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_order_confirmation_email(order):
    """Send order confirmation email to customer"""
    subject = f'Order Confirmation - Order #{order.id}'
    
    # HTML version of the email
    context = {
        'order': order,
        'order_items': order.items.all(),
        'company_name': 'Eshop',
        'support_email': 'support@eshop.com',
        'currency': 'Ksh'
    }
    
    html_message = render_to_string('emails/order_confirmation_email.html', context)
    
    # Plain text version of the email
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject,
            plain_message,
            settings.EMAIL_HOST_USER,
            [order.user.email],
            fail_silently=False,
            html_message=html_message,
        )
        return True
    except Exception as e:
        print(f'Error sending order confirmation email: {e}')
        return False


def send_order_status_update_email(order):
    """Send order status update email to customer"""
    subject = f'Order Status Update - Order #{order.id}'
    
    # Get readable status name from choices
    status_display = dict(order.STATUS_CHOICES).get(order.status, order.status)
    
    # HTML version of the email
    context = {
        'order': order,
        'status_display': status_display,
        'company_name': 'Eshop',
        'support_email': 'support@eshop.com',
        'currency': 'Ksh'
    }
    
    html_message = render_to_string('emails/order_status_update_email.html', context)
    
    # Plain text version of the email
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject,
            plain_message,
            settings.EMAIL_HOST_USER,
            [order.user.email],
            fail_silently=False,
            html_message=html_message,
        )
        return True
    except Exception as e:
        print(f'Error sending order status update email: {e}')
        return False


def send_shipping_confirmation_email(order, tracking_number=None):
    """Send shipping confirmation email with tracking details"""
    subject = f'Shipping Confirmation - Order #{order.id}'
    
    # HTML version of the email
    context = {
        'order': order,
        'tracking_number': tracking_number,
        'company_name': 'Eshop',
        'support_email': 'support@eshop.com',
        'tracking_url': 'https://track.yourcompany.com' if tracking_number else None
    }
    
    html_message = render_to_string('emails/shipping_confirmation_email.html', context)
    
    # Plain text version of the email
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject,
            plain_message,
            settings.EMAIL_HOST_USER,
            [order.user.email],
            fail_silently=False,
            html_message=html_message,
        )
        return True
    except Exception as e:
        print(f'Error sending shipping confirmation email: {e}')
        return False