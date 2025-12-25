#!/bin/bash
# Простой скрипт для создания администратора через SQL
# Использование: bash scripts/create_admin_simple.sh email password

EMAIL="${1}"
PASSWORD="${2}"

if [ -z "$EMAIL" ] || [ -z "$PASSWORD" ]; then
    echo "❌ Ошибка: укажите email и пароль"
    echo "Использование: bash scripts/create_admin_simple.sh <email> <password>"
    exit 1
fi

echo "🔐 Создание администратора..."
echo "Email: $EMAIL"
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
    password_hash = '$HASH',
    updated_at = NOW();
"

echo "📋 SQL команды для выполнения:"
echo ""
echo "--- Вариант 1: Обновить существующего пользователя ---"
echo "$SQL_UPDATE"
echo ""
echo "--- Вариант 2: Создать или обновить (рекомендуется) ---"
echo "$SQL_INSERT"
echo ""
echo "=========================================="
echo ""
echo "🔧 Как выполнить:"
echo ""
echo "1. Подключитесь к серверу:"
echo "   ssh root@89.104.74.123"
echo ""
echo "2. Найдите способ подключиться к PostgreSQL:"
echo "   - Если есть psql: psql -U postgres -d dnevnik_uspekha"
echo "   - Если через Docker: docker exec -it <container> psql -U postgres -d dnevnik_uspekha"
echo "   - Если через systemd: проверьте конфигурацию сервиса"
echo ""
echo "3. Выполните SQL команду (Вариант 2 рекомендуется)"
echo ""
echo "4. Проверьте:"
echo "   SELECT email, role FROM users WHERE email = '$EMAIL';"
echo ""






