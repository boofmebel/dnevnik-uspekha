#!/bin/bash
# Универсальный скрипт установки PostgreSQL

set -e

echo "🐘 УСТАНОВКА POSTGRESQL"
echo "========================"
echo ""

# Определяем ОС
OS="$(uname -s)"
case "${OS}" in
    Linux*)
        if [ -f /etc/debian_version ]; then
            echo "📦 Обнаружена Debian/Ubuntu система"
            echo ""
            echo "Для установки выполните:"
            echo "  sudo apt-get update"
            echo "  sudo apt-get install -y postgresql postgresql-contrib"
            echo "  sudo systemctl start postgresql"
            echo "  sudo systemctl enable postgresql"
            echo "  sudo -u postgres createdb dnevnik_uspekha"
            exit 0
        elif [ -f /etc/redhat-release ]; then
            echo "📦 Обнаружена RedHat/CentOS система"
            echo ""
            echo "Для установки выполните:"
            echo "  sudo yum install -y postgresql-server postgresql-contrib"
            echo "  sudo postgresql-setup --initdb"
            echo "  sudo systemctl start postgresql"
            echo "  sudo systemctl enable postgresql"
            echo "  sudo -u postgres createdb dnevnik_uspekha"
            exit 0
        fi
        ;;
    Darwin*)
        echo "📦 Обнаружена macOS система"
        echo ""
        
        # Проверяем Homebrew
        if command -v brew &> /dev/null; then
            echo "✅ Homebrew найден!"
            echo ""
            echo "Устанавливаю PostgreSQL через Homebrew..."
            brew install postgresql@14
            brew services start postgresql@14
            
            # Ждем запуска
            sleep 3
            
            # Создаем БД
            createdb dnevnik_uspekha 2>/dev/null || echo "⚠️  БД уже существует или нужны права"
            
            echo ""
            echo "✅ PostgreSQL установлен и запущен!"
            echo ""
            echo "Проверка:"
            pg_isready -h localhost || echo "⚠️  PostgreSQL еще запускается, подождите..."
        else
            echo "❌ Homebrew не найден"
            echo ""
            echo "Варианты установки:"
            echo ""
            echo "1. Установить Homebrew:"
            echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            echo ""
            echo "2. Использовать официальный установщик:"
            echo "   https://www.postgresql.org/download/macosx/"
            echo ""
            echo "3. Использовать Docker (если установлен):"
            echo "   ./backend/scripts/start_postgres.sh"
            exit 1
        fi
        ;;
    *)
        echo "⚠️  Неизвестная ОС: ${OS}"
        echo "Установите PostgreSQL вручную"
        exit 1
        ;;
esac

echo ""
echo "✅ Установка завершена!"
echo ""
echo "Проверьте подключение:"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  python scripts/check_setup.py"

