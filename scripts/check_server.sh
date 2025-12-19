#!/bin/bash

# Скрипт для проверки существующего сервера
# Использование: ./scripts/check_server.sh

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SERVER_IP="89.104.74.123"

echo -e "${BLUE}🔍 Проверка сервера $SERVER_IP${NC}"
echo ""

# Проверка доступности
echo -e "${YELLOW}1. Проверка доступности сервера...${NC}"
if ping -c 1 -W 2 "$SERVER_IP" &> /dev/null; then
    echo -e "${GREEN}✅ Сервер доступен${NC}"
else
    echo -e "${RED}❌ Сервер недоступен${NC}"
    exit 1
fi

# Проверка HTTP
echo ""
echo -e "${YELLOW}2. Проверка HTTP...${NC}"
HTTP_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 "http://$SERVER_IP" 2>/dev/null || echo "000")
if [ "$HTTP_RESPONSE" != "000" ]; then
    echo -e "${GREEN}✅ HTTP отвечает (код: $HTTP_RESPONSE)${NC}"
    echo -e "${BLUE}   Содержимое:${NC}"
    curl -s "http://$SERVER_IP" | head -20
else
    echo -e "${RED}❌ HTTP не отвечает${NC}"
fi

# Проверка SSH
echo ""
echo -e "${YELLOW}3. Проверка SSH доступа...${NC}"
echo -e "${BLUE}   Попробуйте подключиться:${NC}"
echo "   ssh root@$SERVER_IP"
echo "   или"
echo "   ssh deploy@$SERVER_IP"
echo ""

# Проверка известных SSH ключей
if [ -f ~/.ssh/id_rsa ] || [ -f ~/.ssh/id_ed25519 ]; then
    echo -e "${YELLOW}4. Попытка подключения с существующими ключами...${NC}"
    
    # Пробуем разные пользователи
    for USER in root deploy ubuntu admin; do
        echo -e "${BLUE}   Пробую: $USER@$SERVER_IP${NC}"
        if ssh -o ConnectTimeout=3 -o StrictHostKeyChecking=no "$USER@$SERVER_IP" "echo 'Успешно'; hostname; pwd" 2>/dev/null; then
            echo -e "${GREEN}✅ Подключение успешно как $USER${NC}"
            echo ""
            echo -e "${BLUE}📋 Информация о сервере:${NC}"
            ssh "$USER@$SERVER_IP" "hostname && pwd && ls -la /var/www 2>/dev/null || ls -la /home 2>/dev/null | head -10"
            break
        fi
    done
else
    echo -e "${YELLOW}⚠️  SSH ключи не найдены${NC}"
fi

echo ""
echo -e "${BLUE}📋 Следующие шаги:${NC}"
echo "1. Подключитесь к серверу: ssh root@$SERVER_IP (или другой пользователь)"
echo "2. Проверьте, где находится проект:"
echo "   find / -name 'dnevnik-uspekha' -o -name 'маркет' 2>/dev/null"
echo "3. Проверьте git репозиторий:"
echo "   cd /путь/к/проекту && git remote -v"
echo "4. Проверьте процессы:"
echo "   ps aux | grep -E 'python|node|nginx'"



