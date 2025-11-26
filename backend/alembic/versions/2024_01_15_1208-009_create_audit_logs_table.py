"""Create audit_logs table

Revision ID: 009
Revises: 008
Create Date: 2024-01-15 12:08:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '009'
down_revision = '008'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('actor_id', sa.Integer(), nullable=False),
        sa.Column('action_type', sa.String(100), nullable=False),
        sa.Column('object_type', sa.String(100), nullable=False),
        sa.Column('object_id', sa.Integer(), nullable=False),
        sa.Column('details', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['actor_id'], ['users.id'], ondelete='CASCADE')
    )
    
    # Create indexes for audit_logs
    op.create_index('ix_audit_logs_id', 'audit_logs', ['id'])
    op.create_index('ix_audit_logs_actor_id', 'audit_logs', ['actor_id'])
    op.create_index('ix_audit_logs_action_type', 'audit_logs', ['action_type'])
    op.create_index('ix_audit_logs_created_at', 'audit_logs', ['created_at'])
    
    # Create composite indexes for efficient querying
    op.create_index('idx_audit_actor_created', 'audit_logs', ['actor_id', sa.text('created_at DESC')])
    op.create_index('idx_audit_action_created', 'audit_logs', ['action_type', sa.text('created_at DESC')])


def downgrade() -> None:
    # Drop audit_logs table
    op.drop_table('audit_logs')
