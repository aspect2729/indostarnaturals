"""Create orders and order_items tables

Revision ID: 007
Revises: 006
Create Date: 2024-01-15 12:06:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create orders table
    op.create_table(
        'orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('order_number', sa.String(100), nullable=False),
        sa.Column('total_amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('discount_amount', sa.Numeric(10, 2), nullable=False, server_default='0.00'),
        sa.Column('final_amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('payment_status', postgresql.ENUM('pending', 'paid', 'failed', 'refunded', name='payment_status', create_type=False), nullable=False, server_default='pending'),
        sa.Column('order_status', postgresql.ENUM('pending', 'confirmed', 'packed', 'out_for_delivery', 'delivered', 'cancelled', 'refunded', name='order_status', create_type=False), nullable=False, server_default='pending'),
        sa.Column('delivery_address_id', sa.Integer(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['delivery_address_id'], ['addresses.id'], ondelete='RESTRICT')
    )
    
    # Create indexes for orders
    op.create_index('ix_orders_id', 'orders', ['id'])
    op.create_index('ix_orders_user_id', 'orders', ['user_id'])
    op.create_index('ix_orders_order_number', 'orders', ['order_number'], unique=True)
    op.create_index('ix_orders_order_status', 'orders', ['order_status'])
    op.create_index('ix_orders_created_at', 'orders', ['created_at'])
    
    # Create composite indexes for efficient querying
    op.create_index('idx_order_user_created', 'orders', ['user_id', sa.text('created_at DESC')])
    op.create_index('idx_order_status_created', 'orders', ['order_status', sa.text('created_at DESC')])
    
    # Create order_items table
    op.create_table(
        'order_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.Numeric(10, 2), nullable=False),
        sa.Column('total_price', sa.Numeric(10, 2), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='RESTRICT')
    )
    
    # Create indexes for order_items
    op.create_index('ix_order_items_id', 'order_items', ['id'])
    op.create_index('ix_order_items_order_id', 'order_items', ['order_id'])
    op.create_index('ix_order_items_product_id', 'order_items', ['product_id'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('order_items')
    op.drop_table('orders')
