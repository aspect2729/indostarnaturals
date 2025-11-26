"""Subscription model"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.enums import SubscriptionFrequency, SubscriptionStatus


class Subscription(Base):
    """Subscription model with frequency and status tracking"""
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    razorpay_subscription_id = Column(String(255), unique=True, nullable=False, index=True)
    plan_frequency = Column(SQLEnum(SubscriptionFrequency), nullable=False)
    start_date = Column(Date, nullable=False)
    next_delivery_date = Column(Date, nullable=False)
    delivery_address_id = Column(Integer, ForeignKey("addresses.id"), nullable=False)
    status = Column(SQLEnum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.ACTIVE, server_default='active', index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, server_default='now()')
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, server_default='now()')

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    product = relationship("Product", foreign_keys=[product_id])
    delivery_address = relationship("Address", foreign_keys=[delivery_address_id])

    def __repr__(self):
        return f"<Subscription(id={self.id}, user_id={self.user_id}, product_id={self.product_id}, status={self.status})>"


# Create composite indexes for efficient querying
Index('idx_subscription_user_status', Subscription.user_id, Subscription.status)
Index('idx_subscription_next_delivery', Subscription.next_delivery_date, Subscription.status)
