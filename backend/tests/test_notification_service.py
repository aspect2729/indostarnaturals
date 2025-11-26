"""Tests for Notification Service

Tests email and SMS sending with retry logic and templates.
"""
import pytest
from unittest.mock import patch, MagicMock
from app.services.notification_service import (
    NotificationService,
    NotificationType,
    NotificationTemplate,
    notification_service
)


class TestNotificationTemplate:
    """Test notification templates"""
    
    def test_order_confirmation_email_template(self):
        """Test order confirmation email template formatting"""
        context = {
            "order_number": "ORD-12345",
            "customer_name": "John Doe",
            "order_total": "1500.00",
            "delivery_address": "123 Main St, City",
            "order_tracking_url": "http://example.com/orders/ORD-12345"
        }
        
        subject, body = NotificationTemplate.get_email_template(
            NotificationType.ORDER_CONFIRMATION,
            context
        )
        
        assert "ORD-12345" in subject
        assert "John Doe" in body
        assert "1500.00" in body
        assert "123 Main St" in body
    
    def test_order_shipped_sms_template(self):
        """Test order shipped SMS template formatting"""
        context = {
            "order_number": "ORD-12345",
            "tracking_info": "TRK-ABC123",
            "expected_delivery": "2024-01-20"
        }
        
        message = NotificationTemplate.get_sms_template(
            NotificationType.ORDER_SHIPPED,
            context
        )
        
        assert "ORD-12345" in message
        assert "TRK-ABC123" in message
        assert "2024-01-20" in message
    
    def test_payment_failed_email_template(self):
        """Test payment failed email template formatting"""
        context = {
            "order_number": "ORD-12345",
            "customer_name": "Jane Smith",
            "order_total": "2500.00",
            "failure_reason": "Insufficient funds",
            "retry_payment_url": "http://example.com/retry"
        }
        
        subject, body = NotificationTemplate.get_email_template(
            NotificationType.PAYMENT_FAILED,
            context
        )
        
        assert "Payment Failed" in subject
        assert "Jane Smith" in body
        assert "Insufficient funds" in body
        assert "retry" in body.lower()


class TestNotificationService:
    """Test notification service"""
    
    def test_exponential_backoff_calculation(self):
        """Test exponential backoff delay calculation"""
        # First retry: 2 seconds
        assert NotificationService._exponential_backoff(0) == 2
        # Second retry: 4 seconds
        assert NotificationService._exponential_backoff(1) == 4
        # Third retry: 8 seconds
        assert NotificationService._exponential_backoff(2) == 8
    
    @patch('app.services.notification_service.settings')
    def test_send_email_dev_mode(self, mock_settings):
        """Test email sending in development mode"""
        mock_settings.EMAIL_PROVIDER = "dev"
        
        result = NotificationService.send_email(
            "test@example.com",
            "Test Subject",
            "Test Body"
        )
        
        assert result is True
    
    @patch('app.services.notification_service.settings')
    def test_send_sms_dev_mode(self, mock_settings):
        """Test SMS sending in development mode"""
        mock_settings.SMS_PROVIDER = "dev"
        
        result = NotificationService.send_sms(
            "+1234567890",
            "Test message"
        )
        
        assert result is True
    
    @patch('app.services.notification_service.settings')
    @patch('app.services.notification_service.time.sleep')
    def test_retry_with_backoff_success_on_second_attempt(self, mock_sleep, mock_settings):
        """Test retry logic succeeds on second attempt"""
        mock_settings.EMAIL_PROVIDER = "dev"
        
        # Create a mock function that fails once then succeeds
        mock_func = MagicMock(side_effect=[False, True])
        
        result = NotificationService._retry_with_backoff(mock_func)
        
        assert result is True
        assert mock_func.call_count == 2
        assert mock_sleep.call_count == 1
        mock_sleep.assert_called_with(2)  # First backoff is 2 seconds
    
    @patch('app.services.notification_service.settings')
    @patch('app.services.notification_service.time.sleep')
    def test_retry_with_backoff_all_attempts_fail(self, mock_sleep, mock_settings):
        """Test retry logic when all attempts fail"""
        mock_settings.EMAIL_PROVIDER = "dev"
        
        # Create a mock function that always fails
        mock_func = MagicMock(return_value=False)
        
        result = NotificationService._retry_with_backoff(mock_func)
        
        assert result is False
        assert mock_func.call_count == 3  # MAX_RETRIES
        assert mock_sleep.call_count == 2  # Sleeps between retries
    
    @patch('app.services.notification_service.settings')
    @patch('app.services.notification_service.time.sleep')
    def test_retry_with_backoff_exception_handling(self, mock_sleep, mock_settings):
        """Test retry logic handles exceptions"""
        mock_settings.EMAIL_PROVIDER = "dev"
        
        # Create a mock function that raises exception twice then succeeds
        mock_func = MagicMock(side_effect=[
            Exception("First failure"),
            Exception("Second failure"),
            True
        ])
        
        result = NotificationService._retry_with_backoff(mock_func)
        
        assert result is True
        assert mock_func.call_count == 3
        assert mock_sleep.call_count == 2
    
    @patch('app.services.notification_service.settings')
    def test_send_order_confirmation(self, mock_settings):
        """Test sending order confirmation notification"""
        mock_settings.EMAIL_PROVIDER = "dev"
        mock_settings.SMS_PROVIDER = "dev"
        mock_settings.FRONTEND_URL = "http://localhost:5173"
        
        email_sent, sms_sent = NotificationService.send_order_confirmation(
            email="customer@example.com",
            phone="+1234567890",
            order_number="ORD-12345",
            customer_name="John Doe",
            order_total="1500.00",
            delivery_address="123 Main St"
        )
        
        assert email_sent is True
        assert sms_sent is True
    
    @patch('app.services.notification_service.settings')
    def test_send_order_shipped(self, mock_settings):
        """Test sending order shipped notification"""
        mock_settings.EMAIL_PROVIDER = "dev"
        mock_settings.SMS_PROVIDER = "dev"
        mock_settings.FRONTEND_URL = "http://localhost:5173"
        
        email_sent, sms_sent = NotificationService.send_order_shipped(
            email="customer@example.com",
            phone="+1234567890",
            order_number="ORD-12345",
            customer_name="John Doe",
            tracking_info="TRK-ABC123",
            expected_delivery="2024-01-20"
        )
        
        assert email_sent is True
        assert sms_sent is True
    
    @patch('app.services.notification_service.settings')
    def test_send_payment_failed(self, mock_settings):
        """Test sending payment failed notification"""
        mock_settings.EMAIL_PROVIDER = "dev"
        mock_settings.FRONTEND_URL = "http://localhost:5173"
        
        result = NotificationService.send_payment_failed(
            email="customer@example.com",
            order_number="ORD-12345",
            customer_name="John Doe",
            order_total="1500.00",
            failure_reason="Insufficient funds"
        )
        
        assert result is True
    
    @patch('app.services.notification_service.settings')
    def test_send_subscription_renewal_reminder(self, mock_settings):
        """Test sending subscription renewal reminder"""
        mock_settings.EMAIL_PROVIDER = "dev"
        mock_settings.FRONTEND_URL = "http://localhost:5173"
        
        result = NotificationService.send_subscription_renewal_reminder(
            email="customer@example.com",
            customer_name="John Doe",
            product_name="Organic Milk",
            frequency="Daily",
            next_delivery_date="2024-01-20",
            amount="150.00",
            subscription_id=1
        )
        
        assert result is True
    
    @patch('app.services.notification_service.settings')
    def test_send_templated_email(self, mock_settings):
        """Test sending templated email"""
        mock_settings.EMAIL_PROVIDER = "dev"
        mock_settings.FRONTEND_URL = "http://localhost:5173"
        
        context = {
            "order_number": "ORD-12345",
            "customer_name": "John Doe",
            "order_total": "1500.00",
            "delivery_address": "123 Main St",
            "order_tracking_url": "http://example.com/orders/ORD-12345"
        }
        
        result = NotificationService.send_templated_email(
            "customer@example.com",
            NotificationType.ORDER_CONFIRMATION,
            context
        )
        
        assert result is True
    
    @patch('app.services.notification_service.settings')
    def test_send_templated_sms(self, mock_settings):
        """Test sending templated SMS"""
        mock_settings.SMS_PROVIDER = "dev"
        mock_settings.FRONTEND_URL = "http://localhost:5173"
        
        context = {
            "order_number": "ORD-12345",
            "customer_name": "John Doe",
            "order_total": "1500.00",
            "short_url": "http://example.com/o/12345"
        }
        
        result = NotificationService.send_templated_sms(
            "+1234567890",
            NotificationType.ORDER_CONFIRMATION,
            context
        )
        
        assert result is True


# Property-Based Tests
from hypothesis import given, strategies as st, settings as hypothesis_settings
from hypothesis import assume
import time


class TestExternalServiceRetryProperties:
    """Property-based tests for external service retry logic"""
    
    # Feature: indostar-naturals-ecommerce, Property 75: External service failures retry with backoff
    @given(
        failure_count=st.integers(min_value=1, max_value=2),
        should_eventually_succeed=st.booleans()
    )
    @hypothesis_settings(max_examples=100, deadline=None)
    @patch('app.services.notification_service.settings')
    @patch('app.services.notification_service.time.sleep')
    def test_external_service_retries_with_exponential_backoff(
        self,
        mock_sleep,
        mock_settings,
        failure_count,
        should_eventually_succeed
    ):
        """
        Property 75: External service failures retry with backoff
        
        For any external service failure (email, SMS), the system should retry
        up to 3 times with exponential backoff (2s, 4s, 8s) before reporting failure.
        
        This test verifies:
        1. The service retries exactly up to MAX_RETRIES (3) times
        2. Exponential backoff is applied between retries (2s, 4s, 8s)
        3. If service succeeds before max retries, it stops retrying
        4. If all retries fail, it returns False
        """
        mock_settings.EMAIL_PROVIDER = "test"
        
        # Create a mock function that fails 'failure_count' times
        if should_eventually_succeed and failure_count < NotificationService.MAX_RETRIES:
            # Fail 'failure_count' times, then succeed
            side_effects = [Exception("Service unavailable")] * failure_count + [True]
        else:
            # Fail all attempts
            side_effects = [Exception("Service unavailable")] * NotificationService.MAX_RETRIES
        
        mock_func = MagicMock(side_effect=side_effects)
        
        # Execute retry logic
        result = NotificationService._retry_with_backoff(mock_func)
        
        # Verify result
        if should_eventually_succeed and failure_count < NotificationService.MAX_RETRIES:
            # Should succeed after 'failure_count' retries
            assert result is True, f"Expected success after {failure_count} failures"
            assert mock_func.call_count == failure_count + 1, \
                f"Expected {failure_count + 1} calls, got {mock_func.call_count}"
            
            # Verify exponential backoff was applied for each retry
            assert mock_sleep.call_count == failure_count, \
                f"Expected {failure_count} sleep calls, got {mock_sleep.call_count}"
            
            # Verify backoff delays: 2s, 4s, 8s
            expected_delays = [NotificationService._exponential_backoff(i) for i in range(failure_count)]
            actual_delays = [call[0][0] for call in mock_sleep.call_args_list]
            assert actual_delays == expected_delays, \
                f"Expected backoff delays {expected_delays}, got {actual_delays}"
        else:
            # Should fail after MAX_RETRIES attempts
            assert result is False, "Expected failure after max retries"
            assert mock_func.call_count == NotificationService.MAX_RETRIES, \
                f"Expected {NotificationService.MAX_RETRIES} calls, got {mock_func.call_count}"
            
            # Verify exponential backoff was applied between all retries
            # With 3 attempts, there should be 2 sleep calls (between attempts)
            assert mock_sleep.call_count == NotificationService.MAX_RETRIES - 1, \
                f"Expected {NotificationService.MAX_RETRIES - 1} sleep calls, got {mock_sleep.call_count}"
            
            # Verify backoff delays: 2s, 4s
            expected_delays = [NotificationService._exponential_backoff(i) for i in range(NotificationService.MAX_RETRIES - 1)]
            actual_delays = [call[0][0] for call in mock_sleep.call_args_list]
            assert actual_delays == expected_delays, \
                f"Expected backoff delays {expected_delays}, got {actual_delays}"
    
    # Feature: indostar-naturals-ecommerce, Property 75: External service failures retry with backoff
    @given(
        email=st.emails(),
        subject=st.text(min_size=1, max_size=100),
        body=st.text(min_size=1, max_size=500)
    )
    @hypothesis_settings(max_examples=100, deadline=None)
    @patch('app.services.notification_service.settings')
    @patch('app.services.notification_service.time.sleep')
    def test_email_service_retries_on_failure(
        self,
        mock_sleep,
        mock_settings,
        email,
        subject,
        body
    ):
        """
        Property 75: Email service retries with exponential backoff
        
        For any email sending attempt that fails, the system should retry
        up to 3 times with exponential backoff before reporting failure.
        """
        mock_settings.EMAIL_PROVIDER = "test"
        
        # Mock the internal send method to fail twice then succeed
        with patch.object(
            NotificationService,
            '_send_email_internal',
            side_effect=[
                Exception("SMTP connection failed"),
                Exception("SMTP timeout"),
                True
            ]
        ):
            result = NotificationService.send_email(email, subject, body)
            
            # Should succeed after 2 failures
            assert result is True
            
            # Should have slept twice (between 3 attempts)
            assert mock_sleep.call_count == 2
            
            # Verify exponential backoff: 2s, 4s
            expected_delays = [2, 4]
            actual_delays = [call[0][0] for call in mock_sleep.call_args_list]
            assert actual_delays == expected_delays
    
    # Feature: indostar-naturals-ecommerce, Property 75: External service failures retry with backoff
    @given(
        phone=st.from_regex(r'\+[1-9]\d{1,14}', fullmatch=True),
        message=st.text(min_size=1, max_size=160)
    )
    @hypothesis_settings(max_examples=100, deadline=None)
    @patch('app.services.notification_service.settings')
    @patch('app.services.notification_service.time.sleep')
    def test_sms_service_retries_on_failure(
        self,
        mock_sleep,
        mock_settings,
        phone,
        message
    ):
        """
        Property 75: SMS service retries with exponential backoff
        
        For any SMS sending attempt that fails, the system should retry
        up to 3 times with exponential backoff before reporting failure.
        """
        mock_settings.SMS_PROVIDER = "test"
        
        # Mock the internal send method to fail all attempts
        with patch.object(
            NotificationService,
            '_send_sms_internal',
            side_effect=[
                Exception("SMS gateway unavailable"),
                Exception("SMS gateway timeout"),
                Exception("SMS gateway error")
            ]
        ):
            result = NotificationService.send_sms(phone, message)
            
            # Should fail after 3 attempts
            assert result is False
            
            # Should have slept twice (between 3 attempts)
            assert mock_sleep.call_count == 2
            
            # Verify exponential backoff: 2s, 4s
            expected_delays = [2, 4]
            actual_delays = [call[0][0] for call in mock_sleep.call_args_list]
            assert actual_delays == expected_delays
    
    # Feature: indostar-naturals-ecommerce, Property 75: External service failures retry with backoff
    @given(
        attempt=st.integers(min_value=0, max_value=10)
    )
    @hypothesis_settings(max_examples=100)
    def test_exponential_backoff_formula(self, attempt):
        """
        Property 75: Exponential backoff calculation
        
        For any retry attempt number, the backoff delay should follow
        the formula: INITIAL_BACKOFF * (2 ** attempt)
        where INITIAL_BACKOFF = 2 seconds
        """
        expected_delay = NotificationService.INITIAL_BACKOFF * (2 ** attempt)
        actual_delay = NotificationService._exponential_backoff(attempt)
        
        assert actual_delay == expected_delay, \
            f"For attempt {attempt}, expected delay {expected_delay}s, got {actual_delay}s"
        
        # Verify the delay increases exponentially
        if attempt > 0:
            previous_delay = NotificationService._exponential_backoff(attempt - 1)
            assert actual_delay == previous_delay * 2, \
                "Delay should double with each attempt"
