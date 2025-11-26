"""Notification background tasks

Handles asynchronous email and SMS sending with retry logic and exponential backoff.
"""
from typing import Dict, Any
from celery import Task
from app.core.celery_app import celery_app
from app.services.notification_service import NotificationService, NotificationType


class NotificationTask(Task):
    """Base task class for notifications with retry logic"""
    
    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 3}
    retry_backoff = True  # Enable exponential backoff
    retry_backoff_max = 600  # Max 10 minutes
    retry_jitter = True  # Add randomness to backoff


@celery_app.task(
    bind=True,
    base=NotificationTask,
    name="app.tasks.notifications.send_email_task"
)
def send_email_task(
    self,
    to_email: str,
    subject: str,
    body: str,
    html_body: str | None = None
) -> bool:
    """
    Send email asynchronously with retry logic.
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Plain text email body
        html_body: Optional HTML email body
        
    Returns:
        True if sent successfully
        
    Raises:
        Exception: If all retry attempts fail
    """
    try:
        result = NotificationService.send_email(
            to_email=to_email,
            subject=subject,
            body=body,
            html_body=html_body
        )
        
        if not result:
            # Raise exception to trigger retry
            raise Exception(f"Failed to send email to {to_email}")
        
        return result
    except Exception as exc:
        # Log the error
        print(f"Error sending email (attempt {self.request.retries + 1}): {exc}")
        # Re-raise to trigger Celery retry
        raise


@celery_app.task(
    bind=True,
    base=NotificationTask,
    name="app.tasks.notifications.send_sms_task"
)
def send_sms_task(
    self,
    phone: str,
    message: str
) -> bool:
    """
    Send SMS asynchronously with retry logic.
    
    Args:
        phone: Phone number to send to
        message: SMS message text
        
    Returns:
        True if sent successfully
        
    Raises:
        Exception: If all retry attempts fail
    """
    try:
        result = NotificationService.send_sms(
            phone=phone,
            message=message
        )
        
        if not result:
            # Raise exception to trigger retry
            raise Exception(f"Failed to send SMS to {phone}")
        
        return result
    except Exception as exc:
        # Log the error
        print(f"Error sending SMS (attempt {self.request.retries + 1}): {exc}")
        # Re-raise to trigger Celery retry
        raise


@celery_app.task(
    bind=True,
    base=NotificationTask,
    name="app.tasks.notifications.send_templated_email_task"
)
def send_templated_email_task(
    self,
    to_email: str,
    notification_type: str,
    context: Dict[str, Any]
) -> bool:
    """
    Send templated email asynchronously with retry logic.
    
    Args:
        to_email: Recipient email address
        notification_type: Type of notification (string value of NotificationType enum)
        context: Template context variables
        
    Returns:
        True if sent successfully
        
    Raises:
        Exception: If all retry attempts fail
    """
    try:
        # Convert string to enum
        notification_type_enum = NotificationType(notification_type)
        
        result = NotificationService.send_templated_email(
            to_email=to_email,
            notification_type=notification_type_enum,
            context=context
        )
        
        if not result:
            raise Exception(f"Failed to send templated email to {to_email}")
        
        return result
    except Exception as exc:
        print(f"Error sending templated email (attempt {self.request.retries + 1}): {exc}")
        raise


@celery_app.task(
    bind=True,
    base=NotificationTask,
    name="app.tasks.notifications.send_templated_sms_task"
)
def send_templated_sms_task(
    self,
    phone: str,
    notification_type: str,
    context: Dict[str, Any]
) -> bool:
    """
    Send templated SMS asynchronously with retry logic.
    
    Args:
        phone: Phone number
        notification_type: Type of notification (string value of NotificationType enum)
        context: Template context variables
        
    Returns:
        True if sent successfully
        
    Raises:
        Exception: If all retry attempts fail
    """
    try:
        # Convert string to enum
        notification_type_enum = NotificationType(notification_type)
        
        result = NotificationService.send_templated_sms(
            phone=phone,
            notification_type=notification_type_enum,
            context=context
        )
        
        if not result:
            raise Exception(f"Failed to send templated SMS to {phone}")
        
        return result
    except Exception as exc:
        print(f"Error sending templated SMS (attempt {self.request.retries + 1}): {exc}")
        raise


@celery_app.task(
    bind=True,
    base=NotificationTask,
    name="app.tasks.notifications.send_order_confirmation_task"
)
def send_order_confirmation_task(
    self,
    email: str,
    phone: str,
    order_number: str,
    customer_name: str,
    order_total: str,
    delivery_address: str
) -> Dict[str, bool]:
    """
    Send order confirmation via email and SMS asynchronously.
    
    Args:
        email: Customer email
        phone: Customer phone
        order_number: Order number
        customer_name: Customer name
        order_total: Order total amount
        delivery_address: Delivery address
        
    Returns:
        Dict with email_sent and sms_sent status
        
    Raises:
        Exception: If both email and SMS fail
    """
    try:
        email_sent, sms_sent = NotificationService.send_order_confirmation(
            email=email,
            phone=phone,
            order_number=order_number,
            customer_name=customer_name,
            order_total=order_total,
            delivery_address=delivery_address
        )
        
        # Consider success if at least one notification was sent
        if not email_sent and not sms_sent:
            raise Exception(f"Failed to send order confirmation for order {order_number}")
        
        return {"email_sent": email_sent, "sms_sent": sms_sent}
    except Exception as exc:
        print(f"Error sending order confirmation (attempt {self.request.retries + 1}): {exc}")
        raise


@celery_app.task(
    bind=True,
    base=NotificationTask,
    name="app.tasks.notifications.send_order_shipped_task"
)
def send_order_shipped_task(
    self,
    email: str,
    phone: str,
    order_number: str,
    customer_name: str,
    tracking_info: str,
    expected_delivery: str
) -> Dict[str, bool]:
    """
    Send order shipped notification via email and SMS asynchronously.
    
    Args:
        email: Customer email
        phone: Customer phone
        order_number: Order number
        customer_name: Customer name
        tracking_info: Tracking information
        expected_delivery: Expected delivery date
        
    Returns:
        Dict with email_sent and sms_sent status
        
    Raises:
        Exception: If both email and SMS fail
    """
    try:
        email_sent, sms_sent = NotificationService.send_order_shipped(
            email=email,
            phone=phone,
            order_number=order_number,
            customer_name=customer_name,
            tracking_info=tracking_info,
            expected_delivery=expected_delivery
        )
        
        # Consider success if at least one notification was sent
        if not email_sent and not sms_sent:
            raise Exception(f"Failed to send order shipped notification for order {order_number}")
        
        return {"email_sent": email_sent, "sms_sent": sms_sent}
    except Exception as exc:
        print(f"Error sending order shipped notification (attempt {self.request.retries + 1}): {exc}")
        raise


@celery_app.task(
    bind=True,
    base=NotificationTask,
    name="app.tasks.notifications.send_payment_failed_task"
)
def send_payment_failed_task(
    self,
    email: str,
    order_number: str,
    customer_name: str,
    order_total: str,
    failure_reason: str
) -> bool:
    """
    Send payment failed notification via email asynchronously.
    
    Args:
        email: Customer email
        order_number: Order number
        customer_name: Customer name
        order_total: Order total amount
        failure_reason: Reason for payment failure
        
    Returns:
        True if sent successfully
        
    Raises:
        Exception: If all retry attempts fail
    """
    try:
        result = NotificationService.send_payment_failed(
            email=email,
            order_number=order_number,
            customer_name=customer_name,
            order_total=order_total,
            failure_reason=failure_reason
        )
        
        if not result:
            raise Exception(f"Failed to send payment failed notification for order {order_number}")
        
        return result
    except Exception as exc:
        print(f"Error sending payment failed notification (attempt {self.request.retries + 1}): {exc}")
        raise


@celery_app.task(
    bind=True,
    base=NotificationTask,
    name="app.tasks.notifications.send_subscription_renewal_reminder_task"
)
def send_subscription_renewal_reminder_task(
    self,
    email: str,
    customer_name: str,
    product_name: str,
    frequency: str,
    next_delivery_date: str,
    amount: str,
    subscription_id: int
) -> bool:
    """
    Send subscription renewal reminder via email asynchronously.
    
    Args:
        email: Customer email
        customer_name: Customer name
        product_name: Product name
        frequency: Subscription frequency
        next_delivery_date: Next delivery date
        amount: Subscription amount
        subscription_id: Subscription ID
        
    Returns:
        True if sent successfully
        
    Raises:
        Exception: If all retry attempts fail
    """
    try:
        result = NotificationService.send_subscription_renewal_reminder(
            email=email,
            customer_name=customer_name,
            product_name=product_name,
            frequency=frequency,
            next_delivery_date=next_delivery_date,
            amount=amount,
            subscription_id=subscription_id
        )
        
        if not result:
            raise Exception(f"Failed to send subscription renewal reminder for subscription {subscription_id}")
        
        return result
    except Exception as exc:
        print(f"Error sending subscription renewal reminder (attempt {self.request.retries + 1}): {exc}")
        raise
