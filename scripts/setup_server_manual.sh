#!/bin/bash
# Скрипт для ручного выполнения на сервере с sudo
# Использование: ssh user@server, затем sudo bash setup_server_manual.sh

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  ПОЛНАЯ НАСТРОЙКА СЕРВЕРА: БД + .ENV                        ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

SERVER_PATH="${SERVER_PATH:-/var/www/dnevnik-uspekha}"
TEST_PATH="${SERVER_PATH}-test"
DB_USER="${DB_USER:-postgres}"
DB_PASSWORD="${DB_PASSWORD:-password}"

# ШАГ 1: Создание БД
echo "📝 ШАГ 1: Создание БД"
echo "───────────────────────────────────────────────────────────────"

# Создаём тестовую БД
echo "Создание dnevnik_test..."
if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw dnevnik_test; then
    echo "   ⚠️  БД dnevnik_test уже существует"
else
    sudo -u postgres psql -c "CREATE DATABASE dnevnik_test;" && echo "   ✅ БД dnevnik_test создана"
fi

# Создаём продакшн БД
echo "Создание dnevnik_prod..."
if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw dnevnik_prod; then
    echo "   ⚠️  БД dnevnik_prod уже существует"
else
    sudo -u postgres psql -c "CREATE DATABASE dnevnik_prod;" && echo "   ✅ БД dnevnik_prod создана"
fi

echo ""

# ШАГ 2: Настройка .env файлов
echo "📝 ШАГ 2: Настройка .env файлов"
echo "───────────────────────────────────────────────────────────────"

# .env для тестового окружения
echo "Создание .env для тестового окружения..."
mkdir -p "$TEST_PATH/backend"
cat > "$TEST_PATH/backend/.env" << ENVEOF
# Тестовое окружение (dev ветка)
ENVIRONMENT=development
DATABASE_URL=postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@localhost:5432/dnevnik_test
SECRET_KEY=\${SECRET_KEY:-your-secret-key-here-change-in-production}
ADMIN_PHONE=79059510009
ALLOWED_ORIGINS=["http://localhost:8000","http://89.104.74.123:8080"]
LOG_LEVEL=INFO
LOG_FORMAT=json
ENVEOF
echo "   ✅ $TEST_PATH/backend/.env"

# .env для продакшн окружения
echo "Создание .env для продакшн окружения..."
mkdir -p "$SERVER_PATH/backend"
cat > "$SERVER_PATH/backend/.env" << ENVEOF
# Продакшн окружение (main ветка)
ENVIRONMENT=production
DATABASE_URL=postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@localhost:5432/dnevnik_prod
SECRET_KEY=\${SECRET_KEY:-your-secret-key-here-change-in-production}
ADMIN_PHONE=79059510009
ALLOWED_ORIGINS=["https://89.104.74.123","http://89.104.74.123"]
LOG_LEVEL=INFO
LOG_FORMAT=json
ENVEOF
echo "   ✅ $SERVER_PATH/backend/.env"

echo ""

# Итог
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  ✅ НАСТРОЙКА ЗАВЕРШЕНА!                                    ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Созданные БД:"
sudo -u postgres psql -c "\l" | grep dnevnik || echo "   (проверьте вручную)"
echo ""
echo "📁 Созданные .env файлы:"
ls -la "$TEST_PATH/backend/.env" 2>/dev/null && echo "   ✅ Тестовое окружение" || echo "   ⚠️  Тестовое окружение не найдено"
ls -la "$SERVER_PATH/backend/.env" 2>/dev/null && echo "   ✅ Продакшн окружение" || echo "   ⚠️  Продакшн окружение не найдено"
echo ""



