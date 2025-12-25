#!/bin/bash

# Версия скрипта, которая использует переменные окружения
# Использование:
#   export SERVER_HOST="123.45.67.89"
#   export SERVER_USER="deploy"
#   export SERVER_PATH="/var/www/dnevnik-uspekha"
#   export SERVER_PORT="22"
#   ./scripts/setup_auto_deploy_env.sh

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

REPO="boofmebel/dnevnik-uspekha"

echo -e "${BLUE}🚀 Настройка автоматического деплоя (через переменные окружения)${NC}"
echo ""

# Проверка переменных окружения
if [ -z "$SERVER_HOST" ] || [ -z "$SERVER_USER" ] || [ -z "$SERVER_PATH" ]; then
    echo -e "${RED}❌ Не заданы обязательные переменные окружения${NC}"
    echo ""
    echo "Использование:"
    echo "  export SERVER_HOST=\"123.45.67.89\""
    echo "  export SERVER_USER=\"deploy\""
    echo "  export SERVER_PATH=\"/var/www/dnevnik-uspekha\""
    echo "  export SERVER_PORT=\"22\"  # опционально"
    echo "  ./scripts/setup_auto_deploy_env.sh"
    exit 1
fi

SERVER_PORT=${SERVER_PORT:-22}

echo -e "${GREEN}Данные сервера:${NC}"
echo "  HOST: $SERVER_HOST"
echo "  USER: $SERVER_USER"
echo "  PATH: $SERVER_PATH"
echo "  PORT: $SERVER_PORT"
echo ""

# Проверка gh CLI
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

# Создание SSH ключа
SSH_KEY_PATH="$HOME/.ssh/id_ed25519_github_deploy"

if [ ! -f "$SSH_KEY_PATH" ]; then
    echo -e "${YELLOW}Создание SSH ключа...${NC}"
    ssh-keygen -t ed25519 -C "github-actions-deploy" -f "$SSH_KEY_PATH" -N "" -q
    echo -e "${GREEN}✅ SSH ключ создан${NC}"
else
    echo -e "${GREEN}✅ SSH ключ уже существует${NC}"
fi

SSH_PRIVATE_KEY=$(cat "$SSH_KEY_PATH")
SSH_PUBLIC_KEY=$(cat "${SSH_KEY_PATH}.pub")

echo ""
echo -e "${BLUE}📋 Публичный ключ (добавьте на сервер):${NC}"
echo "$SSH_PUBLIC_KEY"
echo ""
echo -e "${YELLOW}Команда для добавления ключа:${NC}"
echo "ssh-copy-id -i ${SSH_KEY_PATH}.pub $SERVER_USER@$SERVER_HOST"
echo ""

# Добавление секретов
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
echo -e "${BLUE}📋 Следующие шаги:${NC}"
echo ""
echo "1. Добавьте SSH ключ на сервер:"
echo "   ssh-copy-id -i ${SSH_KEY_PATH}.pub $SERVER_USER@$SERVER_HOST"
echo ""
echo "2. Подготовьте сервер:"
echo "   ssh $SERVER_USER@$SERVER_HOST"
echo "   mkdir -p $SERVER_PATH"
echo "   cd $SERVER_PATH"
echo "   git clone https://github.com/$REPO.git ."
echo ""
echo "3. Протестируйте деплой:"
echo "   git push origin main"
echo ""
echo "4. Проверьте результат:"
echo "   https://github.com/$REPO/actions"
echo ""






