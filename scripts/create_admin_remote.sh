#!/bin/bash
# Скрипт для создания администратора на удалённом сервере
# Использование: bash scripts/create_admin_remote.sh email password

SERVER="root@89.104.74.123"
SERVER_PATH="/var/www/dnevnik-uspekha"

EMAIL="${1}"
PASSWORD="${2}"

if [ -z "$EMAIL" ] || [ -z "$PASSWORD" ]; then
    echo "❌ Ошибка: укажите email и пароль"
    echo "Использование: bash scripts/create_admin_remote.sh <email> <password>"
    exit 1
fi

echo "🔐 Создание администратора на сервере..."
echo "Email: $EMAIL"
echo ""

# Проверяем доступ к серверу
echo "🔍 Проверка подключения к серверу..."
if ! ssh $SERVER "echo 'Connected'" > /dev/null 2>&1; then
    echo "❌ Ошибка: не удалось подключиться к серверу"
    exit 1
fi
echo "✅ Подключение установлено"
echo ""

# Вариант 1: Через Python скрипт
echo "📝 Попытка создать через Python скрипт..."
if ssh $SERVER "cd $SERVER_PATH && python3 scripts/create_admin.py '$EMAIL' '$PASSWORD' 2>&1"; then
    echo ""
    echo "✅ Администратор создан!"
    echo ""
    echo "📋 Следующие шаги:"
    echo "1. Откройте: http://89.104.74.123:3000"
    echo "2. Войдите с email: $EMAIL"
    echo "3. Откройте: http://89.104.74.123:3000/admin.html"
    exit 0
fi

echo ""
echo "⚠️  Python скрипт не сработал, пробуем через SQL..."
echo ""

# Вариант 2: Через SQL (если есть доступ к PostgreSQL)
echo "📝 Генерация SQL команды..."

# Генерируем хеш пароля локально
HASH=$(python3 -c "
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
print(pwd_context.hash('$PASSWORD'))
" 2>/dev/null)

if [ -z "$HASH" ]; then
    echo "❌ Не удалось сгенерировать хеш пароля"
    echo "Установите: pip install passlib[bcrypt]"
    exit 1
fi

# SQL команда
SQL="
DO \$\$
BEGIN
    IF EXISTS(SELECT 1 FROM users WHERE email = '$EMAIL') THEN
        UPDATE users 
        SET role = 'admin', password_hash = '$HASH', updated_at = NOW()
        WHERE email = '$EMAIL';
    ELSE
        INSERT INTO users (email, password_hash, role, created_at)
        VALUES ('$EMAIL', '$HASH', 'admin', NOW());
    END IF;
END
\$\$;
"

echo "📋 SQL команда для выполнения:"
echo "----------------------------------------"
echo "$SQL"
echo "----------------------------------------"
echo ""
echo "Для выполнения подключитесь к PostgreSQL:"
echo "  ssh $SERVER"
echo "  psql -U postgres -d dnevnik_uspekha"
echo "  # Затем вставьте SQL команду выше"
echo ""

