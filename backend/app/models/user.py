"""User model"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.enums import UserRole, DistributorStatus


class User(Base):
    """User model with role-based access control"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=True, index=True)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=True)
    role = Column(SQLEnum(UserRole, values_callable=lambda x: [e.value for e in x]), nullable=False)
    google_id = Column(String(255), unique=True, nullable=True, index=True)
    is_email_verified = Column(Boolean, nullable=False, default=False, server_default='false')
    is_phone_verified = Column(Boolean, nullable=False, default=False, server_default='false')
    is_active = Column(Boolean, nullable=False, default=True, server_default='true')
    distributor_status = Column(SQLEnum(DistributorStatus, values_callable=lambda x: [e.value for e in x]), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, server_default='now()')
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, server_default='now()')

    # Relationships
    addresses = relationship("Address", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, phone={self.phone}, role={self.role})>"
