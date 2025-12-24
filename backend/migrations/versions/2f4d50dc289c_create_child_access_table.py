"""create_child_access_table

Revision ID: 2f4d50dc289c
Revises: e07352965a3e
Create Date: 2025-12-24 22:20:46.654152

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2f4d50dc289c'
down_revision = 'cd2c4f5d51ab'  # Создаем таблицу после последней миграции
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Создание таблицы child_access для хранения PIN и QR-токенов детей
    op.create_table(
        'child_access',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('child_id', sa.Integer(), nullable=False),
        sa.Column('pin_hash', sa.String(), nullable=True),  # Зашифрованный PIN (bcrypt)
        sa.Column('qr_token', sa.String(), nullable=True),  # Уникальный токен для QR-кода
        sa.Column('qr_token_expires_at', sa.DateTime(timezone=True), nullable=True),  # Срок действия QR-токена
        sa.Column('qr_token_valid_from', sa.DateTime(timezone=True), nullable=True),  # Время начала действия (для временного окна)
        sa.Column('qr_token_used_at', sa.DateTime(timezone=True), nullable=True),  # Время использования (одноразовое использование)
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),  # Можно отключить доступ
        sa.Column('failed_attempts', sa.Integer(), nullable=False, server_default='0'),  # Количество неудачных попыток
        sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True),  # Блокировка до определённого времени
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['child_id'], ['children.id'], ),
        sa.UniqueConstraint('child_id'),  # Один доступ на одного ребёнка
    )
    
    # Создание индексов
    op.create_index(op.f('ix_child_access_id'), 'child_access', ['id'], unique=False)
    op.create_index(op.f('ix_child_access_child_id'), 'child_access', ['child_id'], unique=True)
    op.create_index(op.f('ix_child_access_qr_token'), 'child_access', ['qr_token'], unique=True)
    op.create_index('ix_child_access_qr_token_used_at', 'child_access', ['qr_token_used_at'], unique=False)


def downgrade() -> None:
    # Удаление индексов
    op.drop_index('ix_child_access_qr_token_used_at', table_name='child_access')
    op.drop_index(op.f('ix_child_access_qr_token'), table_name='child_access')
    op.drop_index(op.f('ix_child_access_child_id'), table_name='child_access')
    op.drop_index(op.f('ix_child_access_id'), table_name='child_access')
    
    # Удаление таблицы
    op.drop_table('child_access')

