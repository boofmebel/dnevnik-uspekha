#!/bin/bash
# Скрипт для создания администратора для конкретного пользователя
# Использование: bash scripts/create_admin_for_user.sh email password

EMAIL="${1:-79059510009@mail.ru}"
PASSWORD="${2:-Admin123!}"

echo "🔐 Создание администратора для: $EMAIL"
echo ""

# Генерируем хеш пароля
echo "📝 Генерация хеша пароля..."
HASH=$(python3 -c "
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
print(pwd_context.hash('$PASSWORD'))
" 2>/dev/null)

if [ -z "$HASH" ]; then
    echo "❌ Ошибка: не удалось сгенерировать хеш пароля"
    echo "Установите: pip install passlib[bcrypt]"
    exit 1
fi

echo "✅ Хеш пароля сгенерирован"
echo ""

# SQL команды
SQL_CHECK="SELECT id, email, role FROM users WHERE email = '$EMAIL';"

SQL_UPDATE="
UPDATE users 
SET role = 'admin', 
    password_hash = '$HASH',
    updated_at = NOW()
WHERE email = '$EMAIL';
"

SQL_INSERT="
INSERT INTO users (email, password_hash, role, created_at)
VALUES ('$EMAIL', '$HASH', 'admin', NOW())
ON CONFLICT (email) DO UPDATE
SET role = 'admin', 
    password_hash = EXCLUDED.password_hash,
    updated_at = NOW();
"

echo "=========================================="
echo "📋 SQL КОМАНДЫ"
echo "=========================================="
echo ""
echo "1. Проверка существующего пользователя:"
echo "$SQL_CHECK"
echo ""
echo "2. Обновление существующего пользователя (если есть):"
echo "$SQL_UPDATE"
echo ""
echo "3. Создание или обновление (рекомендуется):"
echo "$SQL_INSERT"
echo ""
echo "=========================================="
echo ""
echo "🔧 ВЫПОЛНЕНИЕ:"
echo ""
echo "Подключитесь к базе данных и выполните команду #3:"
echo ""
echo "  ssh root@89.104.74.123"
echo "  psql -U postgres -d dnevnik_uspekha"
echo ""
echo "Затем скопируйте и выполните SQL команду #3 выше"
echo ""
echo "=========================================="
echo ""
echo "📝 Данные для входа:"
echo "  Email: $EMAIL"
echo "  Пароль: $PASSWORD"
echo ""
echo "После выполнения SQL:"
echo "  1. Откройте: http://89.104.74.123:3000"
echo "  2. Войдите с email и паролем выше"
echo "  3. Откройте: http://89.104.74.123:3000/admin.html"
echo ""

