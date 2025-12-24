"""add_qr_token_restrictions_one_time_use

Revision ID: e07352965a3e
Revises: cd2c4f5d51ab
Create Date: 2025-12-24 22:16:34.046769

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e07352965a3e'
down_revision = '2f4d50dc289c'  # Добавляем поля к уже созданной таблице child_access
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Поля qr_token_valid_from и qr_token_used_at уже созданы в миграции 2f4d50dc289c
    # Индекс ix_child_access_qr_token_used_at тоже уже создан
    # Эта миграция оставлена для совместимости, но фактически ничего не делает
    pass


def downgrade() -> None:
    # Поля удаляются вместе с таблицей в миграции 2f4d50dc289c
    pass

