"""Create initial owner account

Revision ID: 003
Revises: 002
Create Date: 2024-01-15 12:02:00.000000

"""
from alembic import op
import sqlalchemy as sa
import bcrypt


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create initial owner account
    # Default credentials: phone=+919999999999, password=admin123
    # IMPORTANT: Change these credentials after first login
    hashed_password = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Use parameterized query to prevent SQL injection
    from sqlalchemy import text
    conn = op.get_bind()
    conn.execute(
        text("""
            INSERT INTO users (
                email, phone, name, hashed_password, role, 
                is_email_verified, is_phone_verified, is_active
            ) VALUES (
                :email,
                :phone,
                :name,
                :hashed_password,
                :role,
                :is_email_verified,
                :is_phone_verified,
                :is_active
            )
        """),
        {
            "email": "owner@indostarnaturals.com",
            "phone": "+919999999999",
            "name": "System Owner",
            "hashed_password": hashed_password,
            "role": "owner",
            "is_email_verified": True,
            "is_phone_verified": True,
            "is_active": True,
        }
    )


def downgrade() -> None:
    op.execute("""
        DELETE FROM users WHERE phone = '+919999999999' AND role = 'owner';
    """)
