#!/bin/bash

# Скрипт для автоматической настройки nginx на сервере
# Использование: ./setup_nginx.sh [server_user@server_host]

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

SERVER="${1:-root@89.104.74.123}"
PROD_PATH="/var/www/dnevnik-uspekha"
TEST_PATH="/var/www/dnevnik-uspekha-test"

echo -e "${BLUE}🔧 Настройка nginx на сервере...${NC}\n"

# Команды для выполнения на сервере
ssh "$SERVER" << 'EOF'
set -e

echo "📦 Проверка nginx..."
if ! command -v nginx >/dev/null 2>&1; then
    echo "Установка nginx..."
    if command -v apt-get >/dev/null 2>&1; then
        sudo apt-get update
        sudo apt-get install -y nginx
    elif command -v yum >/dev/null 2>&1; then
        sudo yum install -y nginx
    else
        echo "❌ Не удалось определить пакетный менеджер"
        exit 1
    fi
fi

# Создаем директории
echo "📁 Создание директорий..."
sudo mkdir -p /var/www/dnevnik-uspekha
sudo mkdir -p /var/www/dnevnik-uspekha-test
sudo chown -R $USER:$USER /var/www/dnevnik-uspekha
sudo chown -R $USER:$USER /var/www/dnevnik-uspekha-test

# Клонируем репозитории если нужно
if [ ! -d /var/www/dnevnik-uspekha/.git ]; then
    echo "📥 Клонирование продакшн репозитория..."
    cd /var/www/dnevnik-uspekha
    git clone https://github.com/boofmebel/dnevnik-uspekha.git . || true
    git checkout main 2>/dev/null || true
fi

if [ ! -d /var/www/dnevnik-uspekha-test/.git ]; then
    echo "📥 Клонирование тестового репозитория..."
    cd /var/www/dnevnik-uspekha-test
    git clone https://github.com/boofmebel/dnevnik-uspekha.git . || true
    git checkout dev 2>/dev/null || true
fi

echo "✅ Директории готовы"
EOF

# Копируем конфигурацию nginx
echo -e "${BLUE}📋 Копирование конфигурации nginx...${NC}"
scp nginx.conf "$SERVER:/tmp/nginx-dnevnik-uspekha.conf"

# Устанавливаем конфигурацию
ssh "$SERVER" << 'EOF'
set -e

echo "📝 Установка конфигурации nginx..."
sudo cp /tmp/nginx-dnevnik-uspekha.conf /etc/nginx/sites-available/dnevnik-uspekha

# Создаем симлинк если не существует
if [ ! -L /etc/nginx/sites-enabled/dnevnik-uspekha ]; then
    sudo ln -s /etc/nginx/sites-available/dnevnik-uspekha /etc/nginx/sites-enabled/
fi

# Проверяем конфигурацию
echo "🔍 Проверка конфигурации..."
if sudo nginx -t; then
    echo "✅ Конфигурация корректна"
    sudo systemctl reload nginx
    echo "✅ Nginx перезапущен"
else
    echo "❌ Ошибка в конфигурации nginx"
    exit 1
fi

echo "✅ Nginx настроен!"
EOF

echo -e "\n${GREEN}✅ Настройка завершена!${NC}\n"
echo -e "${BLUE}🔗 Ссылки:${NC}"
echo -e "   Продакшн: ${GREEN}http://89.104.74.123${NC}"
echo -e "   Тест:     ${YELLOW}http://89.104.74.123/test${NC}"

