"""add settings fields and family rules

Revision ID: 002
Revises: 001
Create Date: 2025-01-18 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Добавляем новые поля в таблицу settings
    op.add_column('settings', sa.Column('max_daily_tasks', sa.Integer(), nullable=False, server_default='10'))
    op.add_column('settings', sa.Column('stars_per_task', sa.Integer(), nullable=False, server_default='1'))
    
    # Создаём таблицу family_rules
    op.create_table(
        'family_rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('rules', sa.Text(), nullable=False, server_default='[]'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_family_rules_user_id'), 'family_rules', ['user_id'], unique=False)


def downgrade():
    # Удаляем индекс и таблицу family_rules
    op.drop_index(op.f('ix_family_rules_user_id'), table_name='family_rules')
    op.drop_table('family_rules')
    
    # Удаляем поля из settings
    op.drop_column('settings', 'stars_per_task')
    op.drop_column('settings', 'max_daily_tasks')



