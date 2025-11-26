"""Product model"""
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Numeric, Index
from sqlalchemy.orm import relationship
from app.core.database import Base


class Product(Base):
    """Product model with dual pricing (consumer and distributor)"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    sku = Column(String(100), unique=True, nullable=False, index=True)
    unit_size = Column(String(100), nullable=False)
    consumer_price = Column(Numeric(10, 2), nullable=False)
    distributor_price = Column(Numeric(10, 2), nullable=False)
    stock_quantity = Column(Integer, nullable=False, default=0)
    is_subscription_available = Column(Boolean, nullable=False, default=False, server_default='false')
    is_active = Column(Boolean, nullable=False, default=True, server_default='true', index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, server_default='now()')
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, server_default='now()')

    # Relationships
    owner = relationship("User", foreign_keys=[owner_id])
    category = relationship("Category", back_populates="products")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan", order_by="ProductImage.display_order")

    def __repr__(self):
        return f"<Product(id={self.id}, title={self.title}, sku={self.sku})>"


# Create composite index for category_id and is_active for efficient filtering
Index('idx_product_category_active', Product.category_id, Product.is_active)
