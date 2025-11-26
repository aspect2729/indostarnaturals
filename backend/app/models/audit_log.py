"""AuditLog model"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from app.core.database import Base


class AuditLog(Base):
    """Audit log model for tracking system changes"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    action_type = Column(String(100), nullable=False, index=True)
    object_type = Column(String(100), nullable=False)
    object_id = Column(Integer, nullable=False)
    details = Column(JSON, nullable=False)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, server_default='now()', index=True)

    # Relationships
    actor = relationship("User", foreign_keys=[actor_id])

    def __repr__(self):
        return f"<AuditLog(id={self.id}, actor_id={self.actor_id}, action_type={self.action_type}, object_type={self.object_type})>"


# Create composite indexes for efficient querying
Index('idx_audit_actor_created', AuditLog.actor_id, AuditLog.created_at.desc())
Index('idx_audit_action_created', AuditLog.action_type, AuditLog.created_at.desc())
