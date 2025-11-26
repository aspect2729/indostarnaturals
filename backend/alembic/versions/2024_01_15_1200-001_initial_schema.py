"""Initial schema with system roles

Revision ID: 001
Revises: 
Create Date: 2024-01-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types
    op.execute("""
        CREATE TYPE user_role AS ENUM ('consumer', 'distributor', 'owner');
    """)
    
    op.execute("""
        CREATE TYPE payment_status AS ENUM ('pending', 'paid', 'failed', 'refunded');
    """)
    
    op.execute("""
        CREATE TYPE order_status AS ENUM (
            'pending', 'confirmed', 'packed', 'out_for_delivery', 
            'delivered', 'cancelled', 'refunded'
        );
    """)
    
    op.execute("""
        CREATE TYPE subscription_frequency AS ENUM ('daily', 'alternate_days', 'weekly');
    """)
    
    op.execute("""
        CREATE TYPE subscription_status AS ENUM ('active', 'paused', 'cancelled');
    """)


def downgrade() -> None:
    op.execute("DROP TYPE IF EXISTS subscription_status;")
    op.execute("DROP TYPE IF EXISTS subscription_frequency;")
    op.execute("DROP TYPE IF EXISTS order_status;")
    op.execute("DROP TYPE IF EXISTS payment_status;")
    op.execute("DROP TYPE IF EXISTS user_role;")
