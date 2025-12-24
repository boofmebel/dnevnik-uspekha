"""create staff_users table

Revision ID: 003_create_staff_users
Revises: 002
Create Date: 2025-12-20

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003_create_staff_users'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Создание таблицы staff_users
    op.create_table(
        'staff_users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('two_fa_secret', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_staff_users_id'), 'staff_users', ['id'], unique=False)
    op.create_index(op.f('ix_staff_users_email'), 'staff_users', ['email'], unique=True)


def downgrade() -> None:
    # Удаление таблицы staff_users
    op.drop_index(op.f('ix_staff_users_email'), table_name='staff_users')
    op.drop_index(op.f('ix_staff_users_id'), table_name='staff_users')
    op.drop_table('staff_users')


