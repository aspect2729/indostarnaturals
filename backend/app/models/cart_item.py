"""CartItem model"""
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.core.database import Base


class CartItem(Base):
    """CartItem model with locked unit price"""
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Numeric(10, 2), nullable=False)  # Locked price at time of adding
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, server_default='now()')

    # Relationships
    cart = relationship("Cart", back_populates="items")
    product = relationship("Product", foreign_keys=[product_id])

    def __repr__(self):
        return f"<CartItem(id={self.id}, cart_id={self.cart_id}, product_id={self.product_id}, quantity={self.quantity})>"
