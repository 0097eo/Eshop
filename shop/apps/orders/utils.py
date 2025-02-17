from django.conf import settings
from django.core.mail import send_mail

def send_order_confirmation_email(order):
    """Send order confirmation email to customer"""
    subject = f'Order Confirmation - Order #{order.id}'
    body = f"""
        Thank you for your order!

        Order Details:
        Order Number: {order.id}
        Total Amount: ${order.total_price}
        Shipping Address: {order.shipping_address}

        Order Status: {order.status}

        Thank you for shopping with us!
    """
    
    try:
        send_mail(
            subject,
            body,
            settings.EMAIL_HOST_USER,
            [order.user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f'Error sending order confirmation email: {e}')
        return False

def send_order_status_update_email(order):
    """Send order status update email to customer"""
    subject = f'Order Status Update - Order #{order.id}'
    body = f"""
        Your order status has been updated.

        Order Details:
        Order Number: {order.id}
        New Status: {order.status}
        Total Amount: ${order.total_price}
        Shipping Address: {order.shipping_address}

        Thank you for shopping with us!
    """
    
    try:
        send_mail(
            subject,
            body,
            settings.EMAIL_HOST_USER,
            [order.user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f'Error sending order status update email: {e}')
        return False

def send_shipping_confirmation_email(order, tracking_number=None):
    """Send shipping confirmation email with tracking details"""
    subject = f'Shipping Confirmation - Order #{order.id}'
    
    tracking_info = f"\nTracking Number: {tracking_number}" if tracking_number else ""
    
    body = f"""
            Your order has been shipped!

            Order Details:
            Order Number: {order.id}
            Status: {order.status}
            Shipping Address: {order.shipping_address}{tracking_info}

            Thank you for shopping with us!
        """
    
    try:
        send_mail(
            subject,
            body,
            settings.EMAIL_HOST_USER,
            [order.user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f'Error sending shipping confirmation email: {e}')
        return False