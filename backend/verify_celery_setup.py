"""
Verification script for Celery setup

This script verifies that all Celery tasks are properly configured and discoverable.
Run this script to ensure the background task system is set up correctly.

Usage:
    python verify_celery_setup.py
"""
import sys
sys.path.insert(0, '.')

def verify_celery_setup():
    """Verify Celery configuration and task registration"""
    
    print("=" * 60)
    print("Celery Setup Verification")
    print("=" * 60)
    print()
    
    # 1. Import Celery app
    print("1. Importing Celery app...")
    try:
        from app.core.celery_app import celery_app
        print("   ✓ Celery app imported successfully")
    except Exception as e:
        print(f"   ✗ Failed to import Celery app: {e}")
        return False
    
    # 2. Check broker connection
    print("\n2. Checking broker configuration...")
    try:
        broker_url = celery_app.conf.broker_url
        print(f"   ✓ Broker URL: {broker_url}")
    except Exception as e:
        print(f"   ✗ Failed to get broker URL: {e}")
        return False
    
    # 3. Check task routes
    print("\n3. Checking task routes...")
    try:
        task_routes = celery_app.conf.task_routes
        print(f"   ✓ Task routes configured: {len(task_routes)} routes")
        for pattern, config in task_routes.items():
            print(f"     - {pattern} → {config['queue']}")
    except Exception as e:
        print(f"   ✗ Failed to get task routes: {e}")
        return False
    
    # 4. Check beat schedule
    print("\n4. Checking Celery Beat schedule...")
    try:
        beat_schedule = celery_app.conf.beat_schedule
        print(f"   ✓ Scheduled tasks: {len(beat_schedule)}")
        for task_name, config in beat_schedule.items():
            print(f"     - {task_name}")
            print(f"       Task: {config['task']}")
            print(f"       Schedule: {config['schedule']}")
    except Exception as e:
        print(f"   ✗ Failed to get beat schedule: {e}")
        return False
    
    # 5. Import and verify notification tasks
    print("\n5. Verifying notification tasks...")
    try:
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
        notification_tasks = [
            "send_email_task",
            "send_sms_task",
            "send_templated_email_task",
            "send_templated_sms_task",
            "send_order_confirmation_task",
            "send_order_shipped_task",
            "send_payment_failed_task",
            "send_subscription_renewal_reminder_task",
        ]
        print(f"   ✓ {len(notification_tasks)} notification tasks imported")
        for task_name in notification_tasks:
            print(f"     - {task_name}")
    except Exception as e:
        print(f"   ✗ Failed to import notification tasks: {e}")
        return False
    
    # 6. Import and verify subscription tasks
    print("\n6. Verifying subscription tasks...")
    try:
        from app.tasks.subscriptions import (
            process_due_subscriptions,
            process_single_subscription,
            send_subscription_renewal_reminders,
        )
        subscription_tasks = [
            "process_due_subscriptions",
            "process_single_subscription",
            "send_subscription_renewal_reminders",
        ]
        print(f"   ✓ {len(subscription_tasks)} subscription tasks imported")
        for task_name in subscription_tasks:
            print(f"     - {task_name}")
    except Exception as e:
        print(f"   ✗ Failed to import subscription tasks: {e}")
        return False
    
    # 7. Import and verify cleanup tasks
    print("\n7. Verifying cleanup tasks...")
    try:
        from app.tasks.cleanup import (
            cleanup_expired_carts,
            cleanup_expired_tokens,
            cleanup_old_audit_logs,
            cleanup_abandoned_sessions,
        )
        cleanup_tasks = [
            "cleanup_expired_carts",
            "cleanup_expired_tokens",
            "cleanup_old_audit_logs",
            "cleanup_abandoned_sessions",
        ]
        print(f"   ✓ {len(cleanup_tasks)} cleanup tasks imported")
        for task_name in cleanup_tasks:
            print(f"     - {task_name}")
    except Exception as e:
        print(f"   ✗ Failed to import cleanup tasks: {e}")
        return False
    
    # 8. Check registered tasks
    print("\n8. Checking registered tasks in Celery...")
    try:
        registered_tasks = list(celery_app.tasks.keys())
        # Filter out built-in Celery tasks
        app_tasks = [t for t in registered_tasks if t.startswith('app.tasks.')]
        print(f"   ✓ {len(app_tasks)} application tasks registered")
        for task in sorted(app_tasks):
            print(f"     - {task}")
    except Exception as e:
        print(f"   ✗ Failed to get registered tasks: {e}")
        return False
    
    # 9. Verify task configuration
    print("\n9. Verifying task configuration...")
    try:
        print(f"   ✓ Task serializer: {celery_app.conf.task_serializer}")
        print(f"   ✓ Result serializer: {celery_app.conf.result_serializer}")
        print(f"   ✓ Timezone: {celery_app.conf.timezone}")
        print(f"   ✓ Task time limit: {celery_app.conf.task_time_limit}s")
        print(f"   ✓ Task soft time limit: {celery_app.conf.task_soft_time_limit}s")
        print(f"   ✓ Worker prefetch multiplier: {celery_app.conf.worker_prefetch_multiplier}")
        print(f"   ✓ Task acks late: {celery_app.conf.task_acks_late}")
        print(f"   ✓ Task default retry delay: {celery_app.conf.task_default_retry_delay}s")
        print(f"   ✓ Task max retries: {celery_app.conf.task_max_retries}")
    except Exception as e:
        print(f"   ✗ Failed to verify task configuration: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✓ All verifications passed!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Start Redis: redis-server")
    print("2. Start Celery worker: celery -A app.core.celery_app worker --loglevel=info")
    print("3. Start Celery beat: celery -A app.core.celery_app beat --loglevel=info")
    print("4. Monitor with Flower: celery -A app.core.celery_app flower --port=5555")
    print()
    
    return True


if __name__ == "__main__":
    success = verify_celery_setup()
    sys.exit(0 if success else 1)
