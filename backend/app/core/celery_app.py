"""Celery application configuration"""
from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

celery_app = Celery(
    "indostar_naturals",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.notifications", "app.tasks.subscriptions", "app.tasks.cleanup"],
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    # Task retry policies
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_default_retry_delay=60,  # 1 minute
    task_max_retries=3,
)

# Task routing - route tasks to specific queues
celery_app.conf.task_routes = {
    "app.tasks.notifications.*": {"queue": "notifications"},
    "app.tasks.subscriptions.*": {"queue": "subscriptions"},
    "app.tasks.cleanup.*": {"queue": "default"},
}

# Scheduled tasks (Celery Beat)
celery_app.conf.beat_schedule = {
    "process-due-subscriptions": {
        "task": "app.tasks.subscriptions.process_due_subscriptions",
        "schedule": crontab(hour=0, minute=0),  # Run daily at midnight UTC
    },
    "cleanup-expired-carts": {
        "task": "app.tasks.cleanup.cleanup_expired_carts",
        "schedule": crontab(hour=2, minute=0),  # Run daily at 2 AM UTC
    },
    "cleanup-expired-tokens": {
        "task": "app.tasks.cleanup.cleanup_expired_tokens",
        "schedule": crontab(hour=3, minute=0),  # Run daily at 3 AM UTC
    },
}
