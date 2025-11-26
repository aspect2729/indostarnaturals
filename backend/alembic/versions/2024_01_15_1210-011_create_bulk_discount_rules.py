"""create bulk discount rules table

Revision ID: 011
Revises: 010
Create Date: 2024-01-15 12:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '011'
down_revision = '010'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create bulk_discount_rules table
    op.create_table(
        'bulk_discount_rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=True),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.Column('min_quantity', sa.Integer(), nullable=False),
        sa.Column('discount_percentage', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], )
    )
    
    # Create indexes
    op.create_index('idx_bulk_discount_product', 'bulk_discount_rules', ['product_id', 'is_active'])
    op.create_index('idx_bulk_discount_category', 'bulk_discount_rules', ['category_id', 'is_active'])
    op.create_index(op.f('ix_bulk_discount_rules_id'), 'bulk_discount_rules', ['id'])
    op.create_index(op.f('ix_bulk_discount_rules_product_id'), 'bulk_discount_rules', ['product_id'])
    op.create_index(op.f('ix_bulk_discount_rules_category_id'), 'bulk_discount_rules', ['category_id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_bulk_discount_rules_category_id'), table_name='bulk_discount_rules')
    op.drop_index(op.f('ix_bulk_discount_rules_product_id'), table_name='bulk_discount_rules')
    op.drop_index(op.f('ix_bulk_discount_rules_id'), table_name='bulk_discount_rules')
    op.drop_index('idx_bulk_discount_category', table_name='bulk_discount_rules')
    op.drop_index('idx_bulk_discount_product', table_name='bulk_discount_rules')
    
    # Drop table
    op.drop_table('bulk_discount_rules')
