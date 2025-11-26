"""Order model"""
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Numeric, Enum as SQLEnum, Index
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.enums import PaymentStatus, OrderStatus


class Order(Base):
    """Order model with status tracking"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    order_number = Column(String(100), unique=True, nullable=False, index=True)
    total_amount = Column(Numeric(10, 2), nullable=False)
    discount_amount = Column(Numeric(10, 2), nullable=False, default=Decimal('0.00'), server_default='0.00')
    final_amount = Column(Numeric(10, 2), nullable=False)
    payment_status = Column(SQLEnum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING, server_default='pending')
    order_status = Column(SQLEnum(OrderStatus), nullable=False, default=OrderStatus.PENDING, server_default='pending', index=True)
    delivery_address_id = Column(Integer, ForeignKey("addresses.id"), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, server_default='now()', index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, server_default='now()')

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    delivery_address = relationship("Address", foreign_keys=[delivery_address_id])
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Order(id={self.id}, order_number={self.order_number}, user_id={self.user_id}, status={self.order_status})>"


# Create composite indexes for efficient querying
Index('idx_order_user_created', Order.user_id, Order.created_at.desc())
Index('idx_order_status_created', Order.order_status, Order.created_at.desc())
