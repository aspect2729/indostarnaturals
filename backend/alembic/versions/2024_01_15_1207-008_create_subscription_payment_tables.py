"""Create subscriptions and payments tables

Revision ID: 008
Revises: 007
Create Date: 2024-01-15 12:07:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create subscriptions table
    op.create_table(
        'subscriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('razorpay_subscription_id', sa.String(255), nullable=False),
        sa.Column('plan_frequency', postgresql.ENUM('daily', 'alternate_days', 'weekly', name='subscription_frequency', create_type=False), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('next_delivery_date', sa.Date(), nullable=False),
        sa.Column('delivery_address_id', sa.Integer(), nullable=False),
        sa.Column('status', postgresql.ENUM('active', 'paused', 'cancelled', name='subscription_status', create_type=False), nullable=False, server_default='active'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['delivery_address_id'], ['addresses.id'], ondelete='RESTRICT')
    )
    
    # Create indexes for subscriptions
    op.create_index('ix_subscriptions_id', 'subscriptions', ['id'])
    op.create_index('ix_subscriptions_user_id', 'subscriptions', ['user_id'])
    op.create_index('ix_subscriptions_razorpay_subscription_id', 'subscriptions', ['razorpay_subscription_id'], unique=True)
    op.create_index('ix_subscriptions_status', 'subscriptions', ['status'])
    
    # Create composite indexes for efficient querying
    op.create_index('idx_subscription_user_status', 'subscriptions', ['user_id', 'status'])
    op.create_index('idx_subscription_next_delivery', 'subscriptions', ['next_delivery_date', 'status'])
    
    # Create payments table
    op.create_table(
        'payments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=True),
        sa.Column('subscription_id', sa.Integer(), nullable=True),
        sa.Column('razorpay_payment_id', sa.String(255), nullable=False),
        sa.Column('razorpay_order_id', sa.String(255), nullable=True),
        sa.Column('amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('currency', sa.String(10), nullable=False, server_default='INR'),
        sa.Column('status', postgresql.ENUM('pending', 'paid', 'failed', 'refunded', name='payment_status', create_type=False), nullable=False, server_default='pending'),
        sa.Column('payment_method', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['subscription_id'], ['subscriptions.id'], ondelete='CASCADE')
    )
    
    # Create indexes for payments
    op.create_index('ix_payments_id', 'payments', ['id'])
    op.create_index('ix_payments_order_id', 'payments', ['order_id'])
    op.create_index('ix_payments_subscription_id', 'payments', ['subscription_id'])
    op.create_index('ix_payments_razorpay_payment_id', 'payments', ['razorpay_payment_id'], unique=True)
    op.create_index('ix_payments_razorpay_order_id', 'payments', ['razorpay_order_id'])
    op.create_index('ix_payments_status', 'payments', ['status'])
    op.create_index('ix_payments_created_at', 'payments', ['created_at'])
    
    # Create composite indexes for efficient querying
    op.create_index('idx_payment_order_status', 'payments', ['order_id', 'status'])
    op.create_index('idx_payment_subscription_status', 'payments', ['subscription_id', 'status'])
    op.create_index('idx_payment_created_status', 'payments', [sa.text('created_at DESC'), 'status'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('payments')
    op.drop_table('subscriptions')
