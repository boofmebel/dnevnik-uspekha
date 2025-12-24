"""add_phone_to_staff_users

Revision ID: cd2c4f5d51ab
Revises: 003_create_staff_users
Create Date: 2025-12-20 17:26:38.695577

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cd2c4f5d51ab'
down_revision = '003_create_staff_users'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Добавляем колонку phone (сначала nullable для существующих записей)
    op.add_column('staff_users', sa.Column('phone', sa.String(length=20), nullable=True))
    
    # Создаём индекс для phone
    op.create_index(op.f('ix_staff_users_phone'), 'staff_users', ['phone'], unique=False)
    
    # Заполняем phone для существующих записей (можно из ADMIN_PHONE или оставить NULL)
    # Если нужно заполнить из .env, это можно сделать отдельным скриптом
    
    # Делаем phone NOT NULL (после заполнения данных)
    # ВАЖНО: Если есть существующие записи без phone, нужно их заполнить перед этим шагом
    # op.alter_column('staff_users', 'phone', nullable=False)
    
    # Делаем email nullable
    op.alter_column('staff_users', 'email', nullable=True)


def downgrade() -> None:
    # Возвращаем email обратно в NOT NULL
    op.alter_column('staff_users', 'email', nullable=False)
    
    # Удаляем индекс и колонку phone
    op.drop_index(op.f('ix_staff_users_phone'), table_name='staff_users')
    op.drop_column('staff_users', 'phone')

