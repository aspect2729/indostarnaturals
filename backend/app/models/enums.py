"""Enumeration types for database models"""
from enum import Enum


class UserRole(str, Enum):
    """User role enumeration"""
    CONSUMER = "consumer"
    DISTRIBUTOR = "distributor"
    OWNER = "owner"


class PaymentStatus(str, Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class OrderStatus(str, Enum):
    """Order status enumeration"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PACKED = "packed"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class SubscriptionFrequency(str, Enum):
    """Subscription frequency enumeration"""
    DAILY = "daily"
    ALTERNATE_DAYS = "alternate_days"
    WEEKLY = "weekly"


class SubscriptionStatus(str, Enum):
    """Subscription status enumeration"""
    ACTIVE = "active"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class DistributorStatus(str, Enum):
    """Distributor approval status enumeration"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
