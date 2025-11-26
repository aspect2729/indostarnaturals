"""Celery background tasks"""

# Import all tasks to make them discoverable by Celery
from app.tasks.notifications import (
    send_email_task,
    send_sms_task,
    send_templated_email_task,
    send_templated_sms_task,
    send_order_confirmation_task,
    send_order_shipped_task,
    send_payment_failed_task,
    send_subscription_renewal_reminder_task,
)

from app.tasks.subscriptions import (
    process_due_subscriptions,
    process_single_subscription,
    send_subscription_renewal_reminders,
)

from app.tasks.cleanup import (
    cleanup_expired_carts,
    cleanup_expired_tokens,
    cleanup_old_audit_logs,
    cleanup_abandoned_sessions,
)

__all__ = [
    # Notification tasks
    "send_email_task",
    "send_sms_task",
    "send_templated_email_task",
    "send_templated_sms_task",
    "send_order_confirmation_task",
    "send_order_shipped_task",
    "send_payment_failed_task",
    "send_subscription_renewal_reminder_task",
    # Subscription tasks
    "process_due_subscriptions",
    "process_single_subscription",
    "send_subscription_renewal_reminders",
    # Cleanup tasks
    "cleanup_expired_carts",
    "cleanup_expired_tokens",
    "cleanup_old_audit_logs",
    "cleanup_abandoned_sessions",
]
