"""Notification Service

Handles email and SMS notifications with template support and retry logic.
Implements exponential backoff for external service failures.
"""
import time
from typing import Optional, Dict, Any
from enum import Enum
from app.core.config import settings


class NotificationType(Enum):
    """Notification types"""
    ORDER_CONFIRMATION = "order_confirmation"
    ORDER_SHIPPED = "order_shipped"
    PAYMENT_FAILED = "payment_failed"
    SUBSCRIPTION_RENEWAL = "subscription_renewal"
    DISTRIBUTOR_APPROVED = "distributor_approved"
    PASSWORD_RESET = "password_reset"
    EMAIL_VERIFICATION = "email_verification"


class NotificationTemplate:
    """Base class for notification templates"""
    
    @staticmethod
    def get_email_template(notification_type: NotificationType, context: Dict[str, Any]) -> tuple[str, str]:
        """
        Get email subject and body for a notification type.
        
        Args:
            notification_type: Type of notification
            context: Template context variables
            
        Returns:
            Tuple of (subject, body)
        """
        templates = {
            NotificationType.ORDER_CONFIRMATION: (
                "Order Confirmation - #{order_number}",
                """
Dear {customer_name},

Thank you for your order! Your order has been confirmed.

Order Number: {order_number}
Order Total: ₹{order_total}
Delivery Address: {delivery_address}

You can track your order status at: {order_tracking_url}

Thank you for shopping with IndoStar Naturals!

Best regards,
IndoStar Naturals Team
                """.strip()
            ),
            NotificationType.ORDER_SHIPPED: (
                "Your Order is On the Way - #{order_number}",
                """
Dear {customer_name},

Great news! Your order has been shipped and is on its way to you.

Order Number: {order_number}
Tracking Information: {tracking_info}

Expected Delivery: {expected_delivery}

Track your order: {order_tracking_url}

Thank you for choosing IndoStar Naturals!

Best regards,
IndoStar Naturals Team
                """.strip()
            ),
            NotificationType.PAYMENT_FAILED: (
                "Payment Failed - Action Required",
                """
Dear {customer_name},

We were unable to process your payment for order #{order_number}.

Order Total: ₹{order_total}
Reason: {failure_reason}

Please retry your payment at: {retry_payment_url}

If you continue to experience issues, please contact our support team.

Best regards,
IndoStar Naturals Team
                """.strip()
            ),
            NotificationType.SUBSCRIPTION_RENEWAL: (
                "Subscription Renewal Reminder",
                """
Dear {customer_name},

Your subscription for {product_name} will be renewed in 24 hours.

Subscription Details:
- Product: {product_name}
- Frequency: {frequency}
- Next Delivery: {next_delivery_date}
- Amount: ₹{amount}

Manage your subscription: {subscription_url}

Thank you for being a valued subscriber!

Best regards,
IndoStar Naturals Team
                """.strip()
            ),
            NotificationType.DISTRIBUTOR_APPROVED: (
                "Distributor Account Approved",
                """
Dear {distributor_name},

Congratulations! Your distributor account has been approved.

You now have access to wholesale pricing and distributor features.

Login to your account: {login_url}

Welcome to the IndoStar Naturals distributor network!

Best regards,
IndoStar Naturals Team
                """.strip()
            ),
            NotificationType.PASSWORD_RESET: (
                "Reset Your Password",
                """
Dear User,

You requested a password reset for your IndoStar Naturals account.

Click here to reset your password: {reset_url}

This link will expire in 24 hours.

If you didn't request this, please ignore this email.

Best regards,
IndoStar Naturals Team
                """.strip()
            ),
            NotificationType.EMAIL_VERIFICATION: (
                "Verify Your Email Address",
                """
Dear User,

Welcome to IndoStar Naturals!

Please verify your email address by clicking the link below:

{verification_url}

This link will expire in 24 hours.

Best regards,
IndoStar Naturals Team
                """.strip()
            ),
        }
        
        subject_template, body_template = templates.get(
            notification_type,
            ("Notification from IndoStar Naturals", "{message}")
        )
        
        # Format templates with context
        subject = subject_template.format(**context)
        body = body_template.format(**context)
        
        return subject, body
    
    @staticmethod
    def get_sms_template(notification_type: NotificationType, context: Dict[str, Any]) -> str:
        """
        Get SMS message for a notification type.
        
        Args:
            notification_type: Type of notification
            context: Template context variables
            
        Returns:
            SMS message text
        """
        templates = {
            NotificationType.ORDER_CONFIRMATION: (
                "IndoStar Naturals: Your order #{order_number} has been confirmed. "
                "Total: ₹{order_total}. Track at {short_url}"
            ),
            NotificationType.ORDER_SHIPPED: (
                "IndoStar Naturals: Your order #{order_number} has been shipped! "
                "Track: {tracking_info}. Expected delivery: {expected_delivery}"
            ),
            NotificationType.PAYMENT_FAILED: (
                "IndoStar Naturals: Payment failed for order #{order_number}. "
                "Please retry at {short_url}"
            ),
            NotificationType.SUBSCRIPTION_RENEWAL: (
                "IndoStar Naturals: Your {product_name} subscription renews in 24 hours. "
                "Amount: ₹{amount}"
            ),
        }
        
        template = templates.get(
            notification_type,
            "IndoStar Naturals: {message}"
        )
        
        return template.format(**context)


class NotificationService:
    """Service for sending notifications with retry logic"""
    
    MAX_RETRIES = 3
    INITIAL_BACKOFF = 2  # seconds
    
    @staticmethod
    def _exponential_backoff(attempt: int) -> float:
        """
        Calculate exponential backoff delay.
        
        Args:
            attempt: Retry attempt number (0-indexed)
            
        Returns:
            Delay in seconds
        """
        return NotificationService.INITIAL_BACKOFF * (2 ** attempt)
    
    @staticmethod
    def _retry_with_backoff(func, *args, **kwargs) -> bool:
        """
        Execute function with exponential backoff retry logic.
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            True if successful, False if all retries failed
        """
        for attempt in range(NotificationService.MAX_RETRIES):
            try:
                result = func(*args, **kwargs)
                if result:
                    return True
                
                # If function returned False, retry
                if attempt < NotificationService.MAX_RETRIES - 1:
                    delay = NotificationService._exponential_backoff(attempt)
                    print(f"Retry attempt {attempt + 1} after {delay}s delay")
                    time.sleep(delay)
            except Exception as e:
                print(f"Error on attempt {attempt + 1}: {e}")
                if attempt < NotificationService.MAX_RETRIES - 1:
                    delay = NotificationService._exponential_backoff(attempt)
                    print(f"Retrying after {delay}s delay")
                    time.sleep(delay)
                else:
                    print(f"All {NotificationService.MAX_RETRIES} attempts failed")
                    return False
        
        return False
    
    @staticmethod
    def send_email(
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> bool:
        """
        Send email with retry logic and exponential backoff.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Plain text email body
            html_body: Optional HTML email body
            
        Returns:
            True if sent successfully after retries
        """
        def _send():
            return NotificationService._send_email_internal(
                to_email, subject, body, html_body
            )
        
        return NotificationService._retry_with_backoff(_send)
    
    @staticmethod
    def _send_email_internal(
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> bool:
        """
        Internal method to send email via configured provider.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Plain text email body
            html_body: Optional HTML email body
            
        Returns:
            True if sent successfully
        """
        if settings.EMAIL_PROVIDER == "sendgrid":
            return NotificationService._send_via_sendgrid(
                to_email, subject, body, html_body
            )
        elif settings.EMAIL_PROVIDER == "ses":
            return NotificationService._send_via_ses(
                to_email, subject, body, html_body
            )
        else:
            # For development/testing
            print(f"[DEV] Email to {to_email}")
            print(f"Subject: {subject}")
            print(f"Body: {body}")
            return True
    
    @staticmethod
    def _send_via_sendgrid(
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> bool:
        """
        Send email via SendGrid.
        
        Args:
            to_email: Recipient email
            subject: Email subject
            body: Plain text body
            html_body: Optional HTML body
            
        Returns:
            True if sent successfully
        """
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail, Content
            
            # Create message with both plain text and HTML
            message = Mail(
                from_email=settings.SENDGRID_FROM_EMAIL,
                to_emails=to_email,
                subject=subject,
                plain_text_content=body
            )
            
            if html_body:
                message.add_content(Content("text/html", html_body))
            
            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
            response = sg.send(message)
            
            return response.status_code == 202
        except Exception as e:
            print(f"Error sending email via SendGrid: {e}")
            raise
    
    @staticmethod
    def _send_via_ses(
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> bool:
        """
        Send email via AWS SES.
        
        Args:
            to_email: Recipient email
            subject: Email subject
            body: Plain text body
            html_body: Optional HTML body
            
        Returns:
            True if sent successfully
        """
        try:
            import boto3
            from botocore.exceptions import ClientError
            
            ses_client = boto3.client(
                'ses',
                region_name=settings.S3_REGION,
                aws_access_key_id=settings.S3_ACCESS_KEY,
                aws_secret_access_key=settings.S3_SECRET_KEY
            )
            
            # Build message body
            body_dict = {'Text': {'Data': body, 'Charset': 'UTF-8'}}
            if html_body:
                body_dict['Html'] = {'Data': html_body, 'Charset': 'UTF-8'}
            
            response = ses_client.send_email(
                Source=settings.SENDGRID_FROM_EMAIL,  # Use same config key
                Destination={'ToAddresses': [to_email]},
                Message={
                    'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                    'Body': body_dict
                }
            )
            
            return 'MessageId' in response
        except ClientError as e:
            print(f"Error sending email via SES: {e}")
            raise
    
    @staticmethod
    def send_sms(phone: str, message: str) -> bool:
        """
        Send SMS with retry logic and exponential backoff.
        
        Args:
            phone: Phone number to send to
            message: SMS message text
            
        Returns:
            True if sent successfully after retries
        """
        def _send():
            return NotificationService._send_sms_internal(phone, message)
        
        return NotificationService._retry_with_backoff(_send)
    
    @staticmethod
    def _send_sms_internal(phone: str, message: str) -> bool:
        """
        Internal method to send SMS via configured provider.
        
        Args:
            phone: Phone number
            message: SMS message
            
        Returns:
            True if sent successfully
        """
        if settings.SMS_PROVIDER == "twilio":
            return NotificationService._send_sms_via_twilio(phone, message)
        elif settings.SMS_PROVIDER == "msg91":
            return NotificationService._send_sms_via_msg91(phone, message)
        else:
            # For development/testing
            print(f"[DEV] SMS to {phone}: {message}")
            return True
    
    @staticmethod
    def _send_sms_via_twilio(phone: str, message: str) -> bool:
        """
        Send SMS via Twilio.
        
        Args:
            phone: Phone number
            message: SMS message
            
        Returns:
            True if sent successfully
        """
        try:
            from twilio.rest import Client
            
            client = Client(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )
            
            msg = client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone
            )
            
            return msg.sid is not None
        except Exception as e:
            print(f"Error sending SMS via Twilio: {e}")
            raise
    
    @staticmethod
    def _send_sms_via_msg91(phone: str, message: str) -> bool:
        """
        Send SMS via MSG91.
        
        Args:
            phone: Phone number
            message: SMS message
            
        Returns:
            True if sent successfully
        """
        try:
            import requests
            
            # MSG91 API implementation
            # Note: This is a basic implementation - adjust based on MSG91 API docs
            url = "https://api.msg91.com/api/v5/flow/"
            
            payload = {
                "flow_id": "your_flow_id",  # Configure in settings
                "sender": "INDSTR",  # Your sender ID
                "mobiles": phone,
                "message": message
            }
            
            headers = {
                "authkey": settings.TWILIO_AUTH_TOKEN,  # Reuse config or add MSG91_API_KEY
                "content-type": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers)
            return response.status_code == 200
        except Exception as e:
            print(f"Error sending SMS via MSG91: {e}")
            raise
    
    @staticmethod
    def send_templated_email(
        to_email: str,
        notification_type: NotificationType,
        context: Dict[str, Any]
    ) -> bool:
        """
        Send email using predefined template.
        
        Args:
            to_email: Recipient email address
            notification_type: Type of notification
            context: Template context variables
            
        Returns:
            True if sent successfully
        """
        subject, body = NotificationTemplate.get_email_template(
            notification_type, context
        )
        return NotificationService.send_email(to_email, subject, body)
    
    @staticmethod
    def send_templated_sms(
        phone: str,
        notification_type: NotificationType,
        context: Dict[str, Any]
    ) -> bool:
        """
        Send SMS using predefined template.
        
        Args:
            phone: Phone number
            notification_type: Type of notification
            context: Template context variables
            
        Returns:
            True if sent successfully
        """
        message = NotificationTemplate.get_sms_template(notification_type, context)
        return NotificationService.send_sms(phone, message)
    
    @staticmethod
    def send_order_confirmation(
        email: str,
        phone: str,
        order_number: str,
        customer_name: str,
        order_total: str,
        delivery_address: str
    ) -> tuple[bool, bool]:
        """
        Send order confirmation via email and SMS.
        
        Args:
            email: Customer email
            phone: Customer phone
            order_number: Order number
            customer_name: Customer name
            order_total: Order total amount
            delivery_address: Delivery address
            
        Returns:
            Tuple of (email_sent, sms_sent)
        """
        context = {
            "order_number": order_number,
            "customer_name": customer_name,
            "order_total": order_total,
            "delivery_address": delivery_address,
            "order_tracking_url": f"{settings.FRONTEND_URL}/orders/{order_number}",
            "short_url": f"{settings.FRONTEND_URL}/orders/{order_number}"
        }
        
        email_sent = NotificationService.send_templated_email(
            email,
            NotificationType.ORDER_CONFIRMATION,
            context
        )
        
        sms_sent = NotificationService.send_templated_sms(
            phone,
            NotificationType.ORDER_CONFIRMATION,
            context
        )
        
        return email_sent, sms_sent
    
    @staticmethod
    def send_order_shipped(
        email: str,
        phone: str,
        order_number: str,
        customer_name: str,
        tracking_info: str,
        expected_delivery: str
    ) -> tuple[bool, bool]:
        """
        Send order shipped notification via email and SMS.
        
        Args:
            email: Customer email
            phone: Customer phone
            order_number: Order number
            customer_name: Customer name
            tracking_info: Tracking information
            expected_delivery: Expected delivery date
            
        Returns:
            Tuple of (email_sent, sms_sent)
        """
        context = {
            "order_number": order_number,
            "customer_name": customer_name,
            "tracking_info": tracking_info,
            "expected_delivery": expected_delivery,
            "order_tracking_url": f"{settings.FRONTEND_URL}/orders/{order_number}"
        }
        
        email_sent = NotificationService.send_templated_email(
            email,
            NotificationType.ORDER_SHIPPED,
            context
        )
        
        sms_sent = NotificationService.send_templated_sms(
            phone,
            NotificationType.ORDER_SHIPPED,
            context
        )
        
        return email_sent, sms_sent
    
    @staticmethod
    def send_payment_failed(
        email: str,
        order_number: str,
        customer_name: str,
        order_total: str,
        failure_reason: str
    ) -> bool:
        """
        Send payment failed notification via email.
        
        Args:
            email: Customer email
            order_number: Order number
            customer_name: Customer name
            order_total: Order total amount
            failure_reason: Reason for payment failure
            
        Returns:
            True if sent successfully
        """
        context = {
            "order_number": order_number,
            "customer_name": customer_name,
            "order_total": order_total,
            "failure_reason": failure_reason,
            "retry_payment_url": f"{settings.FRONTEND_URL}/orders/{order_number}/retry-payment"
        }
        
        return NotificationService.send_templated_email(
            email,
            NotificationType.PAYMENT_FAILED,
            context
        )
    
    @staticmethod
    def send_subscription_renewal_reminder(
        email: str,
        customer_name: str,
        product_name: str,
        frequency: str,
        next_delivery_date: str,
        amount: str,
        subscription_id: int
    ) -> bool:
        """
        Send subscription renewal reminder via email.
        
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
        """
        context = {
            "customer_name": customer_name,
            "product_name": product_name,
            "frequency": frequency,
            "next_delivery_date": next_delivery_date,
            "amount": amount,
            "subscription_url": f"{settings.FRONTEND_URL}/subscriptions/{subscription_id}"
        }
        
        return NotificationService.send_templated_email(
            email,
            NotificationType.SUBSCRIPTION_RENEWAL,
            context
        )


# Create singleton instance
notification_service = NotificationService()
