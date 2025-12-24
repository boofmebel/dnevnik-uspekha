#!/bin/bash
# Скрипт установки PostgreSQL локально для миграции

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  📦 УСТАНОВКА POSTGRESQL ЛОКАЛЬНО                           ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Проверка Homebrew
if ! command -v brew &> /dev/null; then
    echo "📦 Установка Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Добавляем Homebrew в PATH (для Apple Silicon)
    if [ -f /opt/homebrew/bin/brew ]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    elif [ -f /usr/local/bin/brew ]; then
        eval "$(/usr/local/bin/brew shellenv)"
    fi
fi

echo "✅ Homebrew установлен"
echo ""

# Установка PostgreSQL
echo "📦 Установка PostgreSQL@14..."
brew install postgresql@14

echo "✅ PostgreSQL установлен"
echo ""

# Запуск PostgreSQL
echo "🚀 Запуск PostgreSQL..."
brew services start postgresql@14

# Ждём запуска
sleep 3

echo "✅ PostgreSQL запущен"
echo ""

# Создание БД
echo "📝 Создание базы данных dnevnik_uspekha..."
createdb dnevnik_uspekha 2>/dev/null || echo "⚠️  БД уже существует или ошибка создания"

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  ✅ УСТАНОВКА ЗАВЕРШЕНА!                                    ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "Теперь можно выполнить миграцию:"
echo "  cd backend"
echo "  alembic upgrade head"
echo "  python3 ../scripts/migrate_admins_to_staff.py"
echo ""


