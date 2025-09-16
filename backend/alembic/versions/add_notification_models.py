"""Add notification models

Revision ID: add_notification_models
Revises: 
Create Date: 2025-09-16 13:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_notification_models'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create enum type for notification types
    op.execute("""
    CREATE TYPE notificationtype AS ENUM (
        'SYSTEM', 'LOAN_APPROVAL', 'LOAN_REJECTION', 'DONATION_RECEIVED',
        'CAMPAIGN_UPDATE', 'PAYMENT_REMINDER', 'ACCOUNT_UPDATE', 'OTHER'
    )
    """)
    
    # Create notification table
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True, index=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('notification_type', sa.Enum(
            'SYSTEM', 'LOAN_APPROVAL', 'LOAN_REJECTION', 'DONATION_RECEIVED',
            'CAMPAIGN_UPDATE', 'PAYMENT_REMINDER', 'ACCOUNT_UPDATE', 'OTHER',
            name='notificationtype'
        ), nullable=False, server_default='SYSTEM'),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='f'),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True)
    )
    
    # Create user_notification_preferences table
    op.create_table(
        'user_notification_preferences',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True, index=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True, index=True),
        sa.Column('email_enabled', sa.Boolean(), nullable=False, server_default='t'),
        sa.Column('push_enabled', sa.Boolean(), nullable=False, server_default='t'),
        sa.Column('sms_enabled', sa.Boolean(), nullable=False, server_default='f'),
        sa.Column('in_app_enabled', sa.Boolean(), nullable=False, server_default='t'),
        sa.Column('email_frequency', sa.String(length=20), nullable=False, server_default='IMMEDIATE'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False)
    )
    
    # Add indexes
    op.create_index('idx_notifications_user_created', 'notifications', ['user_id', 'created_at'], unique=False)
    op.create_index('idx_notifications_created', 'notifications', ['created_at'], unique=False)
    op.create_index('idx_notifications_is_read', 'notifications', ['is_read'], unique=False)

def downgrade():
    # Drop indexes
    op.drop_index('idx_notifications_is_read', table_name='notifications')
    op.drop_index('idx_notifications_created', table_name='notifications')
    op.drop_index('idx_notifications_user_created', table_name='notifications')
    
    # Drop tables
    op.drop_table('user_notification_preferences')
    op.drop_table('notifications')
    
    # Drop enum type
    op.execute("DROP TYPE notificationtype")
