"""initial_schema_users_and_settings

Revision ID: a192a3299c59
Revises: 
Create Date: 2025-12-20 16:49:12.580500

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a192a3299c59'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Создание таблицы users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['parent_id'], ['users.id'], ),
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_phone'), 'users', ['phone'], unique=True)
    
    # Создание таблицы children
    op.create_table(
        'children',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False, server_default='Ребёнок'),
        sa.Column('gender', sa.Enum('girl', 'boy', 'none', name='gender'), nullable=False, server_default='none'),
        sa.Column('avatar', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    )
    op.create_index(op.f('ix_children_id'), 'children', ['id'], unique=False)
    op.create_index(op.f('ix_children_user_id'), 'children', ['user_id'], unique=False)
    
    # Создание таблицы settings (базовая версия, без полей из миграции 002)
    op.create_table(
        'settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('child_id', sa.Integer(), nullable=False),
        sa.Column('stars_to_money', sa.Integer(), nullable=False, server_default='15'),
        sa.Column('money_per_stars', sa.Numeric(10, 2), nullable=False, server_default='200'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['child_id'], ['children.id'], ),
        sa.UniqueConstraint('child_id'),
    )
    op.create_index(op.f('ix_settings_id'), 'settings', ['id'], unique=False)
    op.create_index(op.f('ix_settings_child_id'), 'settings', ['child_id'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_settings_child_id'), table_name='settings')
    op.drop_index(op.f('ix_settings_id'), table_name='settings')
    op.drop_table('settings')
    op.drop_index(op.f('ix_children_user_id'), table_name='children')
    op.drop_index(op.f('ix_children_id'), table_name='children')
    op.drop_table('children')
    op.drop_index(op.f('ix_users_phone'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')

