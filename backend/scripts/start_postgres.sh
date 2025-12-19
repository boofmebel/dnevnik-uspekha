#!/bin/bash
# Скрипт для запуска PostgreSQL через Docker

echo "🐘 Запуск PostgreSQL через Docker..."

# Проверяем наличие Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не найден"
    echo "💡 Установите Docker Desktop: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Проверяем, запущен ли Docker
if ! docker info &> /dev/null; then
    echo "❌ Docker не запущен"
    echo "💡 Запустите Docker Desktop"
    exit 1
fi

# Переходим в корневую директорию проекта
cd "$(dirname "$0")/../.."

# Запускаем PostgreSQL через docker-compose
if command -v docker-compose &> /dev/null; then
    echo "✅ Запускаю PostgreSQL через docker-compose..."
    docker-compose up -d postgres
elif docker compose version &> /dev/null; then
    echo "✅ Запускаю PostgreSQL через docker compose..."
    docker compose up -d postgres
else
    echo "❌ docker-compose не найден"
    echo "💡 Установите docker-compose или используйте: docker run"
    exit 1
fi

# Ждем пока PostgreSQL запустится
echo "⏳ Ожидание запуска PostgreSQL..."
sleep 5

# Проверяем подключение
if docker exec dnevnik-postgres pg_isready -U postgres &> /dev/null; then
    echo "✅ PostgreSQL запущен и готов к работе!"
    echo ""
    echo "📋 Информация:"
    echo "   Host: localhost"
    echo "   Port: 5432"
    echo "   Database: dnevnik_uspekha"
    echo "   User: postgres"
    echo "   Password: password"
    echo ""
    echo "💡 Теперь можно выполнить миграцию:"
    echo "   cd backend && source venv/bin/activate && alembic upgrade head"
else
    echo "⚠️  PostgreSQL запускается, подождите немного..."
    echo "💡 Проверьте статус: docker ps"
fi

