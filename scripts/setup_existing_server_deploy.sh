#!/bin/bash

# Настройка автоматического деплоя на существующий сервер
# Использование: ./scripts/setup_existing_server_deploy.sh

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

REPO="boofmebel/dnevnik-uspekha"
SERVER_HOST="89.104.74.123"
SERVER_USER="root"
SERVER_PATH="/var/www/dnevnik-uspekha"
SERVER_PORT="22"

echo -e "${BLUE}🚀 Настройка автоматического деплоя на существующий сервер${NC}"
echo ""
echo -e "${GREEN}Данные сервера:${NC}"
echo "  HOST: $SERVER_HOST"
echo "  USER: $SERVER_USER"
echo "  PATH: $SERVER_PATH"
echo "  PORT: $SERVER_PORT"
echo ""

# Проверка GitHub CLI
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI (gh) не установлен${NC}"
    echo ""
    echo "Установите:"
    echo "  brew install gh"
    echo ""
    echo "Затем аутентифицируйтесь:"
    echo "  gh auth login"
    exit 1
fi

# Проверка аутентификации
if ! gh auth status &> /dev/null; then
    echo -e "${YELLOW}Требуется аутентификация в GitHub${NC}"
    gh auth login
fi

echo -e "${GREEN}✅ GitHub CLI готов${NC}"
echo ""

# Используем существующий SSH ключ или создаём новый
SSH_KEY_PATH="$HOME/.ssh/id_rsa"
if [ ! -f "$SSH_KEY_PATH" ]; then
    SSH_KEY_PATH="$HOME/.ssh/id_ed25519_github_deploy"
    if [ ! -f "$SSH_KEY_PATH" ]; then
        echo -e "${YELLOW}Создание SSH ключа...${NC}"
        ssh-keygen -t ed25519 -C "github-actions-deploy" -f "$SSH_KEY_PATH" -N "" -q
        echo -e "${GREEN}✅ SSH ключ создан${NC}"
    fi
fi

SSH_PRIVATE_KEY=$(cat "$SSH_KEY_PATH")

# Проверка, что ключ добавлен на сервер
echo -e "${YELLOW}Проверка SSH доступа...${NC}"
if ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" "echo 'OK'" &> /dev/null; then
    echo -e "${GREEN}✅ SSH доступ работает${NC}"
else
    echo -e "${YELLOW}⚠️  Добавьте публичный ключ на сервер:${NC}"
    echo "   ssh-copy-id -i ${SSH_KEY_PATH}.pub $SERVER_USER@$SERVER_HOST"
    echo ""
    read -p "Нажмите Enter после добавления ключа..."
fi

# Добавление секретов
echo ""
echo -e "${BLUE}Добавление секретов в GitHub...${NC}"
echo ""

echo "$SERVER_HOST" | gh secret set SERVER_HOST --repo "$REPO" && echo -e "${GREEN}✅ SERVER_HOST${NC}" || echo -e "${RED}❌ SERVER_HOST${NC}"
echo "$SERVER_USER" | gh secret set SERVER_USER --repo "$REPO" && echo -e "${GREEN}✅ SERVER_USER${NC}" || echo -e "${RED}❌ SERVER_USER${NC}"
echo "$SSH_PRIVATE_KEY" | gh secret set SERVER_SSH_KEY --repo "$REPO" && echo -e "${GREEN}✅ SERVER_SSH_KEY${NC}" || echo -e "${RED}❌ SERVER_SSH_KEY${NC}"
echo "$SERVER_PATH" | gh secret set SERVER_PATH --repo "$REPO" && echo -e "${GREEN}✅ SERVER_PATH${NC}" || echo -e "${RED}❌ SERVER_PATH${NC}"
echo "$SERVER_PORT" | gh secret set SERVER_PORT --repo "$REPO" && echo -e "${GREEN}✅ SERVER_PORT${NC}" || echo -e "${RED}❌ SERVER_PORT${NC}"

echo ""
echo -e "${GREEN}✅ Все секреты добавлены!${NC}"
echo ""
echo -e "${BLUE}📋 Проверка на сервере...${NC}"

# Проверка git на сервере
ssh "$SERVER_USER@$SERVER_HOST" "cd $SERVER_PATH && git remote -v" 2>/dev/null || echo -e "${YELLOW}⚠️  Git не настроен на сервере${NC}"

echo ""
echo -e "${GREEN}🎉 Автоматический деплой настроен!${NC}"
echo ""
echo -e "${BLUE}📋 Что дальше:${NC}"
echo "1. При push в main будет автоматический деплой"
echo "2. Проверьте результат: https://github.com/$REPO/actions"
echo "3. После деплоя проверьте сайт: http://$SERVER_HOST"
echo ""





