"""add distributor status

Revision ID: 010
Revises: 009
Create Date: 2024-01-15 12:09:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '010'
down_revision = '009'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum type for distributor status
    op.execute("CREATE TYPE distributor_status AS ENUM ('pending', 'approved', 'rejected');")
    
    # Add distributor_status column to users table
    op.add_column('users', sa.Column('distributor_status', postgresql.ENUM('pending', 'approved', 'rejected', name='distributor_status', create_type=False), nullable=True))


def downgrade() -> None:
    # Remove distributor_status column
    op.drop_column('users', 'distributor_status')
    
    # Drop enum type
    op.execute("DROP TYPE IF EXISTS distributor_status;")
