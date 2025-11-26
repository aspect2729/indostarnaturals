"""Cart model"""
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.core.database import Base


class Cart(Base):
    """Cart model with coupon support"""
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    coupon_code = Column(String(100), nullable=True)
    discount_amount = Column(Numeric(10, 2), nullable=False, default=Decimal('0.00'), server_default='0.00')
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, server_default='now()')
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, server_default='now()')

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Cart(id={self.id}, user_id={self.user_id}, items_count={len(self.items) if self.items else 0})>"
