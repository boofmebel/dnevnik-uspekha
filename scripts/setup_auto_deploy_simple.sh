#!/bin/bash

# Упрощённая версия скрипта настройки деплоя
# Использует GitHub CLI (gh) - самый простой способ

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

REPO="boofmebel/dnevnik-uspekha"

echo -e "${BLUE}🚀 Настройка автоматического деплоя (упрощённая версия)${NC}"
echo ""

# Проверка gh CLI
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI (gh) не установлен${NC}"
    echo ""
    echo -e "${YELLOW}Установите GitHub CLI:${NC}"
    echo "  macOS: brew install gh"
    echo "  Linux: https://cli.github.com/manual/installation"
    echo ""
    echo "После установки запустите: gh auth login"
    exit 1
fi

echo -e "${GREEN}✅ GitHub CLI найден${NC}"

# Проверка аутентификации
if ! gh auth status &> /dev/null; then
    echo -e "${YELLOW}Требуется аутентификация в GitHub${NC}"
    gh auth login
fi

echo -e "${GREEN}✅ Аутентифицирован в GitHub${NC}"
echo ""

# Создание SSH ключа
SSH_KEY_PATH="$HOME/.ssh/id_ed25519_github_deploy"

if [ -f "$SSH_KEY_PATH" ]; then
    echo -e "${YELLOW}SSH ключ уже существует: $SSH_KEY_PATH${NC}"
    read -p "Использовать существующий? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        SSH_KEY_PATH="$HOME/.ssh/id_ed25519_github_deploy_$(date +%s)"
        ssh-keygen -t ed25519 -C "github-actions-deploy" -f "$SSH_KEY_PATH" -N ""
        echo -e "${GREEN}✅ Новый SSH ключ создан${NC}"
    fi
else
    echo -e "${YELLOW}Создание SSH ключа...${NC}"
    ssh-keygen -t ed25519 -C "github-actions-deploy" -f "$SSH_KEY_PATH" -N ""
    echo -e "${GREEN}✅ SSH ключ создан: $SSH_KEY_PATH${NC}"
fi

SSH_PRIVATE_KEY=$(cat "$SSH_KEY_PATH")
SSH_PUBLIC_KEY=$(cat "${SSH_KEY_PATH}.pub")

echo ""
echo -e "${BLUE}📋 Публичный ключ (скопируйте его):${NC}"
echo "$SSH_PUBLIC_KEY"
echo ""
echo -e "${YELLOW}⚠️  Добавьте публичный ключ на сервер:${NC}"
echo -e "${BLUE}ssh-copy-id -i ${SSH_KEY_PATH}.pub user@your-server.com${NC}"
echo ""
read -p "Нажмите Enter после добавления ключа на сервер..."

# Получение данных о сервере
echo ""
echo -e "${YELLOW}Введите данные о сервере:${NC}"
echo ""

read -p "SERVER_HOST (IP или домен, например: 123.45.67.89): " SERVER_HOST
read -p "SERVER_USER (пользователь SSH, например: deploy): " SERVER_USER
read -p "SERVER_PATH (путь к проекту, например: /var/www/dnevnik-uspekha): " SERVER_PATH
read -p "SERVER_PORT (SSH порт, Enter для 22): " SERVER_PORT_INPUT

SERVER_PORT=${SERVER_PORT_INPUT:-22}

echo ""
echo -e "${GREEN}Данные сервера:${NC}"
echo "  HOST: $SERVER_HOST"
echo "  USER: $SERVER_USER"
echo "  PATH: $SERVER_PATH"
echo "  PORT: $SERVER_PORT"
echo ""
read -p "Всё правильно? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}Отменено${NC}"
    exit 1
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
echo -e "${BLUE}📋 Следующие шаги:${NC}"
echo ""
echo "1. Убедитесь, что публичный SSH ключ добавлен на сервер:"
echo -e "   ${YELLOW}ssh-copy-id -i ${SSH_KEY_PATH}.pub $SERVER_USER@$SERVER_HOST${NC}"
echo ""
echo "2. На сервере подготовьте проект:"
echo -e "   ${YELLOW}ssh $SERVER_USER@$SERVER_HOST${NC}"
echo -e "   ${YELLOW}mkdir -p $SERVER_PATH${NC}"
echo -e "   ${YELLOW}cd $SERVER_PATH${NC}"
echo -e "   ${YELLOW}git clone https://github.com/$REPO.git .${NC}"
echo ""
echo "3. Сделайте push в main для тестирования:"
echo -e "   ${YELLOW}git push origin main${NC}"
echo ""
echo "4. Проверьте деплой:"
echo -e "   ${BLUE}https://github.com/$REPO/actions${NC}"
echo ""
echo -e "${GREEN}🎉 Автоматический деплой настроен!${NC}"

