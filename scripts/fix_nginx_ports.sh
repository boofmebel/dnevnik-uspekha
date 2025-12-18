#!/bin/bash

# Скрипт для исправления конфликта портов на сервере
# Разделяет проекты по разным портам

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SERVER="root@89.104.74.123"

echo -e "${BLUE}🔧 Исправление конфликта портов на сервере${NC}"
echo ""

# План:
# - MarketAI: остаётся на порту 80 (основной проект)
# - Дневник успеха: переводим на порт 3000 (или можно 8080, но там уже тест)

echo -e "${YELLOW}Текущая ситуация:${NC}"
echo "  - MarketAI: порт 80 (основной)"
echo "  - Дневник успеха: порт 80 (КОНФЛИКТ!)"
echo "  - Дневник успеха (тест): порт 8080"
echo ""

echo -e "${BLUE}План исправления:${NC}"
echo "  - MarketAI: порт 80 (остаётся)"
echo "  - Дневник успеха: порт 3000 (новый)"
echo "  - Дневник успеха (тест): порт 8080 (остаётся)"
echo ""

read -p "Продолжить? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Отменено"
    exit 1
fi

# Создаём резервную копию
echo -e "${YELLOW}Создание резервной копии...${NC}"
ssh "$SERVER" "cp /etc/nginx/sites-available/dnevnik-uspekha /etc/nginx/sites-available/dnevnik-uspekha.backup.$(date +%Y%m%d_%H%M%S)"

# Обновляем конфигурацию nginx для Дневника успеха
echo -e "${YELLOW}Обновление конфигурации nginx...${NC}"
ssh "$SERVER" "cat > /etc/nginx/sites-available/dnevnik-uspekha <<'NGINX_CONFIG'
# Конфигурация Nginx для \"Дневник успеха\"
# ПРОДАКШН (main ветка) - порт 3000
server {
    listen 3000;
    server_name 89.104.74.123;
    
    # Корневая директория проекта
    root /var/www/dnevnik-uspekha;
    index index.html;
    
    # Логи
    access_log /var/log/nginx/dnevnik-uspekha-access.log;
    error_log /var/log/nginx/dnevnik-uspekha-error.log;
    
    # Основная локация
    location / {
        try_files \$uri \$uri/ /index.html;
    }
    
    # Кэширование статических файлов
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control \"public, immutable\";
    }
    
    # Безопасность
    add_header X-Frame-Options \"SAMEORIGIN\" always;
    add_header X-Content-Type-Options \"nosniff\" always;
    add_header X-XSS-Protection \"1; mode=block\" always;
    
    # Запрет доступа к скрытым файлам
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
}

# ТЕСТОВОЕ ОКРУЖЕНИЕ (dev ветка) - порт 8080
server {
    listen 8080;
    server_name 89.104.74.123;
    
    # Корневая директория тестового окружения
    root /var/www/dnevnik-uspekha-test;
    index index.html;
    
    # Логи
    access_log /var/log/nginx/dnevnik-uspekha-test-access.log;
    error_log /var/log/nginx/dnevnik-uspekha-test-error.log;
    
    # Основная локация
    location / {
        try_files \$uri \$uri/ /index.html;
    }
    
    # Кэширование статических файлов
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control \"public, immutable\";
    }
    
    # Безопасность
    add_header X-Frame-Options \"SAMEORIGIN\" always;
    add_header X-Content-Type-Options \"nosniff\" always;
    add_header X-XSS-Protection \"1; mode=block\" always;
    
    # Запрет доступа к скрытым файлам
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
}
NGINX_CONFIG
"

# Проверка конфигурации
echo -e "${YELLOW}Проверка конфигурации nginx...${NC}"
if ssh "$SERVER" "nginx -t" 2>&1 | grep -q "successful"; then
    echo -e "${GREEN}✅ Конфигурация корректна${NC}"
else
    echo -e "${RED}❌ Ошибка в конфигурации${NC}"
    ssh "$SERVER" "nginx -t"
    exit 1
fi

# Перезагрузка nginx
echo -e "${YELLOW}Перезагрузка nginx...${NC}"
ssh "$SERVER" "systemctl reload nginx"

echo ""
echo -e "${GREEN}✅ Конфигурация обновлена!${NC}"
echo ""
echo -e "${BLUE}📋 Новые порты:${NC}"
echo "  - MarketAI: http://89.104.74.123 (порт 80)"
echo "  - Дневник успеха: http://89.104.74.123:3000 (порт 3000)"
echo "  - Дневник успеха (тест): http://89.104.74.123:8080 (порт 8080)"
echo ""

