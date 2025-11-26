"""Add stock quantity constraints

Revision ID: 012
Revises: 011
Create Date: 2024-01-15 12:12:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '012'
down_revision = '011'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add check constraint to ensure stock_quantity is non-negative"""
    # Add check constraint to products table
    op.create_check_constraint(
        'ck_products_stock_quantity_non_negative',
        'products',
        'stock_quantity >= 0'
    )


def downgrade() -> None:
    """Remove stock quantity constraint"""
    op.drop_constraint(
        'ck_products_stock_quantity_non_negative',
        'products',
        type_='check'
    )
