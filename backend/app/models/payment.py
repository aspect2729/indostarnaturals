"""Payment model"""
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Enum as SQLEnum, Index
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.enums import PaymentStatus


class Payment(Base):
    """Payment model with Razorpay integration fields"""
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=True, index=True)
    razorpay_payment_id = Column(String(255), unique=True, nullable=False, index=True)
    razorpay_order_id = Column(String(255), nullable=True, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(10), nullable=False, default='INR', server_default='INR')
    status = Column(SQLEnum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING, server_default='pending', index=True)
    payment_method = Column(String(100), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, server_default='now()', index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, server_default='now()')

    # Relationships
    order = relationship("Order", foreign_keys=[order_id])
    subscription = relationship("Subscription", foreign_keys=[subscription_id])

    def __repr__(self):
        return f"<Payment(id={self.id}, razorpay_payment_id={self.razorpay_payment_id}, amount={self.amount}, status={self.status})>"


# Create composite indexes for efficient querying
Index('idx_payment_order_status', Payment.order_id, Payment.status)
Index('idx_payment_subscription_status', Payment.subscription_id, Payment.status)
Index('idx_payment_created_status', Payment.created_at.desc(), Payment.status)
