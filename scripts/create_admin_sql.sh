#!/bin/bash
# Скрипт для создания администратора через SQL
# Использование: bash scripts/create_admin_sql.sh email password

EMAIL="${1:-admin@example.com}"
PASSWORD="${2:-admin123}"

echo "🔐 Создание администратора через SQL..."
echo ""
echo "Email: $EMAIL"
echo ""

# Генерируем хеш пароля (bcrypt)
echo "📝 Генерация хеша пароля..."
HASH=$(python3 -c "
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
print(pwd_context.hash('$PASSWORD'))
" 2>/dev/null)

if [ -z "$HASH" ]; then
    echo "❌ Ошибка: не удалось сгенерировать хеш пароля"
    echo "Установите passlib: pip install passlib[bcrypt]"
    exit 1
fi

echo "✅ Хеш пароля сгенерирован"
echo ""

# SQL команды
SQL="
-- Проверяем, существует ли пользователь
DO \$\$
DECLARE
    user_exists BOOLEAN;
BEGIN
    SELECT EXISTS(SELECT 1 FROM users WHERE email = '$EMAIL') INTO user_exists;
    
    IF user_exists THEN
        -- Обновляем существующего пользователя
        UPDATE users 
        SET role = 'admin', 
            password_hash = '$HASH',
            updated_at = NOW()
        WHERE email = '$EMAIL';
        RAISE NOTICE 'Пользователь % обновлён и назначен администратором', '$EMAIL';
    ELSE
        -- Создаём нового администратора
        INSERT INTO users (email, password_hash, role, created_at)
        VALUES ('$EMAIL', '$HASH', 'admin', NOW());
        RAISE NOTICE 'Создан новый администратор: %', '$EMAIL';
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
echo "  psql -U your_user -d your_database"
echo ""
echo "Или выполните через SSH:"
echo "  ssh root@89.104.74.123 'psql -U postgres -d dnevnik_uspekha -c \"$SQL\"'"
echo ""






