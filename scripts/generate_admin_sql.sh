#!/bin/bash
# Генерация SQL команды для создания администратора
# Использование: bash scripts/generate_admin_sql.sh email password

EMAIL="${1:-admin@dnevnik-uspekha.ru}"
PASSWORD="${2:-admin123}"

echo "🔐 Генерация SQL команды для создания администратора"
echo "Email: $EMAIL"
echo "Пароль: $PASSWORD"
echo ""
echo "📝 Генерация хеша пароля..."

# Пробуем разные способы генерации хеша
HASH=""

# Способ 1: Python с passlib
if command -v python3 &> /dev/null; then
    HASH=$(python3 -c "
try:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
    print(pwd_context.hash('$PASSWORD'))
except ImportError:
    pass
" 2>/dev/null)
fi

# Способ 2: Python с bcrypt напрямую
if [ -z "$HASH" ] && command -v python3 &> /dev/null; then
    HASH=$(python3 -c "
try:
    import bcrypt
    hashed = bcrypt.hashpw('$PASSWORD'.encode('utf-8'), bcrypt.gensalt())
    print(hashed.decode('utf-8'))
except ImportError:
    pass
" 2>/dev/null)
fi

if [ -z "$HASH" ]; then
    echo "❌ Не удалось сгенерировать хеш пароля"
    echo ""
    echo "Установите один из вариантов:"
    echo "  pip install passlib[bcrypt]"
    echo "  или"
    echo "  pip install bcrypt"
    echo ""
    echo "Или используйте онлайн генератор:"
    echo "  https://bcrypt-generator.com/"
    echo ""
    exit 1
fi

echo "✅ Хеш пароля сгенерирован"
echo ""

# SQL команды
echo "=========================================="
echo "📋 SQL КОМАНДЫ ДЛЯ ВЫПОЛНЕНИЯ"
echo "=========================================="
echo ""
echo "--- Вариант 1: Обновить существующего пользователя ---"
echo ""
echo "UPDATE users"
echo "SET role = 'admin',"
echo "    password_hash = '$HASH',"
echo "    updated_at = NOW()"
echo "WHERE email = '$EMAIL';"
echo ""
echo "--- Вариант 2: Создать или обновить (рекомендуется) ---"
echo ""
echo "INSERT INTO users (email, password_hash, role, created_at)"
echo "VALUES ('$EMAIL', '$HASH', 'admin', NOW())"
echo "ON CONFLICT (email) DO UPDATE"
echo "SET role = 'admin',"
echo "    password_hash = EXCLUDED.password_hash,"
echo "    updated_at = NOW();"
echo ""
echo "--- Вариант 3: Просто обновить роль (если пользователь уже есть) ---"
echo ""
echo "UPDATE users SET role = 'admin' WHERE email = '$EMAIL';"
echo ""
echo "=========================================="
echo ""
echo "🔧 КАК ВЫПОЛНИТЬ:"
echo ""
echo "1. Подключитесь к базе данных PostgreSQL"
echo "2. Выполните одну из SQL команд выше"
echo "3. Проверьте результат:"
echo "   SELECT email, role FROM users WHERE email = '$EMAIL';"
echo ""
echo "=========================================="



