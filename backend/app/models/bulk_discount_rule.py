"""BulkDiscountRule model"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.core.database import Base


class BulkDiscountRule(Base):
    """Bulk discount rule model for distributor orders"""
    __tablename__ = "bulk_discount_rules"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True, index=True)  # Null means applies to all products
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True, index=True)  # Null means applies to all categories
    min_quantity = Column(Integer, nullable=False)
    discount_percentage = Column(Numeric(5, 2), nullable=False)  # e.g., 10.00 for 10%
    is_active = Column(Boolean, nullable=False, default=True, server_default='true')
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, server_default='now()')
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, server_default='now()')

    # Relationships
    product = relationship("Product", foreign_keys=[product_id])
    category = relationship("Category", foreign_keys=[category_id])

    def __repr__(self):
        return f"<BulkDiscountRule(id={self.id}, min_quantity={self.min_quantity}, discount_percentage={self.discount_percentage})>"


# Create indexes for efficient querying
Index('idx_bulk_discount_product', BulkDiscountRule.product_id, BulkDiscountRule.is_active)
Index('idx_bulk_discount_category', BulkDiscountRule.category_id, BulkDiscountRule.is_active)
