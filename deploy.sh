#!/bin/bash

# Скрипт для деплоя на сервер
# Использование: ./deploy.sh [server_user@server_host:/path/to/project]

set -e  # Остановка при ошибке

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Начинаем деплой...${NC}"

# Проверяем что мы на ветке main
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo -e "${RED}❌ Ошибка: вы должны быть на ветке main!${NC}"
    echo -e "${YELLOW}Текущая ветка: $CURRENT_BRANCH${NC}"
    echo -e "${YELLOW}Переключитесь: git checkout main${NC}"
    exit 1
fi

# Проверяем что нет незакоммиченных изменений
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${RED}❌ Ошибка: есть незакоммиченные изменения!${NC}"
    echo -e "${YELLOW}Закоммитьте или отмените изменения перед деплоем${NC}"
    exit 1
fi

# Отправляем изменения на GitHub
echo -e "${GREEN}📤 Отправляем изменения на GitHub...${NC}"
git push origin main

# Если передан параметр сервера, деплоим
if [ -n "$1" ]; then
    SERVER=$1
    echo -e "${GREEN}📦 Деплоим на сервер: $SERVER${NC}"
    
    # Разбираем параметр сервера
    if [[ $SERVER == *":"* ]]; then
        SERVER_USER_HOST="${SERVER%%:*}"
        SERVER_PATH="${SERVER##*:}"
    else
        echo -e "${RED}❌ Неверный формат сервера!${NC}"
        echo -e "${YELLOW}Использование: ./deploy.sh user@host:/path/to/project${NC}"
        exit 1
    fi
    
    # Выполняем деплой через SSH
    ssh $SERVER_USER_HOST "cd $SERVER_PATH && git pull origin main"
    
    echo -e "${GREEN}✅ Деплой завершен успешно!${NC}"
else
    echo -e "${YELLOW}⚠️  Сервер не указан. Изменения отправлены на GitHub.${NC}"
    echo -e "${YELLOW}Для деплоя на сервер используйте:${NC}"
    echo -e "${YELLOW}  ./deploy.sh user@host:/path/to/project${NC}"
fi

