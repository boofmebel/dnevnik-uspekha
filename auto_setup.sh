#!/bin/bash

# Полностью автоматическая настройка деплоя
# Использование: ./auto_setup.sh

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🚀 Автоматическая настройка деплоя${NC}\n"

# Проверка зависимостей
echo -e "${YELLOW}📦 Проверка зависимостей...${NC}"
command -v git >/dev/null 2>&1 || { echo -e "${RED}❌ Git не установлен${NC}"; exit 1; }
command -v curl >/dev/null 2>&1 || { echo -e "${RED}❌ curl не установлен${NC}"; exit 1; }
echo -e "${GREEN}✅ Все зависимости установлены${NC}\n"

# Параметры
SERVER_IP="89.104.74.123"
SERVER_USER="root"
SERVER_PATH="/var/www/dnevnik-uspekha"
REPO="boofmebel/dnevnik-uspekha"

# Запрос GitHub токена
echo -e "${YELLOW}🔑 Нужен GitHub Personal Access Token${NC}"
echo -e "${BLUE}Создайте токен: https://github.com/settings/tokens/new${NC}"
echo -e "${BLUE}Права: repo, workflow${NC}"
read -p "Введите GitHub токен: " GITHUB_TOKEN

if [ -z "$GITHUB_TOKEN" ]; then
    echo -e "${RED}❌ Токен не введен${NC}"
    exit 1
fi

# Запрос SSH данных для сервера
echo -e "\n${YELLOW}🖥️  Настройка доступа к серверу${NC}"
read -p "SSH пользователь [$SERVER_USER]: " input_user
SERVER_USER=${input_user:-$SERVER_USER}

read -sp "SSH пароль (или нажмите Enter если используете ключ): " SSH_PASS
echo ""

# 1. Создание workflow через GitHub API
echo -e "\n${YELLOW}📝 Создание workflow файла через GitHub API...${NC}"

WORKFLOW_CONTENT=$(cat << 'WORKFLOWEOF'
name: Deploy to Server

on:
  push:
    branches:
      - main

jobs:
  deploy:
    name: Deploy to production server
    runs-on: ubuntu-latest
    
    steps:
      - name: Deploy via SSH
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SERVER_SSH_KEY }}
          port: ${{ secrets.SERVER_PORT || 22 }}
          script: |
            echo "🚀 Начинаем деплой..."
            cd ${{ secrets.SERVER_PATH }}
            echo "📥 Получаем последние изменения..."
            git fetch origin
            git reset --hard origin/main
            echo "✅ Деплой завершен успешно!"
WORKFLOWEOF
)

# Кодируем в base64
WORKFLOW_B64=$(echo "$WORKFLOW_CONTENT" | base64)

# Создаем файл через API
RESPONSE=$(curl -s -w "\n%{http_code}" -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  -d "{
    \"message\": \"Add GitHub Actions workflow\",
    \"content\": \"$WORKFLOW_B64\",
    \"branch\": \"main\"
  }" \
  "https://api.github.com/repos/$REPO/contents/.github/workflows/deploy.yml")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "201" ] || [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Workflow файл создан через API${NC}"
else
    echo -e "${YELLOW}⚠️  Не удалось создать через API (код: $HTTP_CODE)${NC}"
    echo -e "${BLUE}Создайте файл вручную через GitHub UI${NC}"
    echo "$WORKFLOW_CONTENT" > WORKFLOW_CONTENT.txt
    echo -e "${GREEN}✅ Содержимое сохранено в WORKFLOW_CONTENT.txt${NC}"
fi

# 2. Настройка Secrets через GitHub API
echo -e "\n${YELLOW}🔐 Настройка Secrets...${NC}"

# Читаем приватный ключ
if [ -f "SSH_PRIVATE_KEY.txt" ]; then
    SSH_KEY=$(cat SSH_PRIVATE_KEY.txt)
else
    SSH_KEY=$(cat ~/.ssh/id_rsa_github_actions 2>/dev/null || echo "")
fi

if [ -z "$SSH_KEY" ]; then
    echo -e "${RED}❌ SSH приватный ключ не найден${NC}"
    echo -e "${YELLOW}Создайте файл SSH_PRIVATE_KEY.txt с приватным ключом${NC}"
    exit 1
fi

# Функция для создания секрета
create_secret() {
    local secret_name=$1
    local secret_value=$2
    
    # GitHub использует публичный ключ репозитория для шифрования
    # Получаем публичный ключ
    KEY_DATA=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$REPO/actions/secrets/public-key")
    
    KEY_ID=$(echo "$KEY_DATA" | grep -o '"key_id":"[^"]*"' | cut -d'"' -f4)
    KEY=$(echo "$KEY_DATA" | grep -o '"key":"[^"]*"' | cut -d'"' -f4)
    
    if [ -z "$KEY" ] || [ -z "$KEY_ID" ]; then
        echo -e "${YELLOW}⚠️  Не удалось получить публичный ключ для $secret_name${NC}"
        return 1
    fi
    
    # Шифруем значение (требует библиотеку sodium)
    # Упрощенный вариант - используем GitHub CLI если доступен
    if command -v gh >/dev/null 2>&1; then
        echo "$secret_value" | gh secret set "$secret_name" --repo "$REPO"
        echo -e "${GREEN}✅ Secret $secret_name создан${NC}"
    else
        echo -e "${YELLOW}⚠️  GitHub CLI не установлен, создайте секрет вручную:${NC}"
        echo -e "${BLUE}  $secret_name = $secret_value${NC}"
    fi
}

# Создаем секреты
echo -e "${BLUE}Создание секретов...${NC}"
create_secret "SERVER_HOST" "$SERVER_IP" || echo "SERVER_HOST: $SERVER_IP"
create_secret "SERVER_USER" "$SERVER_USER" || echo "SERVER_USER: $SERVER_USER"
create_secret "SERVER_SSH_KEY" "$SSH_KEY" || echo "SERVER_SSH_KEY: [содержимое SSH_PRIVATE_KEY.txt]"
create_secret "SERVER_PATH" "$SERVER_PATH" || echo "SERVER_PATH: $SERVER_PATH"

# 3. Настройка сервера
echo -e "\n${YELLOW}🖥️  Настройка сервера...${NC}"

if [ -n "$SSH_PASS" ]; then
    # Используем sshpass если пароль указан
    if ! command -v sshpass >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  sshpass не установлен, настройте сервер вручную${NC}"
    else
        echo -e "${BLUE}Подключение к серверу...${NC}"
        sshpass -p "$SSH_PASS" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" << EOF
            mkdir -p $SERVER_PATH
            cd $SERVER_PATH
            if [ ! -d .git ]; then
                git clone https://github.com/$REPO.git .
            fi
            echo "✅ Сервер настроен"
EOF
    fi
else
    # Используем SSH ключ
    echo -e "${BLUE}Попытка подключения по SSH ключу...${NC}"
    if ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" "echo 'Connected'" 2>/dev/null; then
        ssh "$SERVER_USER@$SERVER_IP" << EOF
            mkdir -p $SERVER_PATH
            cd $SERVER_PATH
            if [ ! -d .git ]; then
                git clone https://github.com/$REPO.git .
            fi
            echo "✅ Сервер настроен"
EOF
        echo -e "${GREEN}✅ Сервер настроен${NC}"
    else
        echo -e "${YELLOW}⚠️  Не удалось подключиться по SSH ключу${NC}"
        echo -e "${BLUE}Настройте сервер вручную:${NC}"
        echo -e "  ssh $SERVER_USER@$SERVER_IP"
        echo -e "  mkdir -p $SERVER_PATH"
        echo -e "  cd $SERVER_PATH"
        echo -e "  git clone https://github.com/$REPO.git ."
    fi
fi

# 4. Добавление публичного ключа на сервер
echo -e "\n${YELLOW}🔑 Настройка SSH ключа на сервере...${NC}"

if [ -f "SSH_PUBLIC_KEY.txt" ]; then
    PUB_KEY=$(cat SSH_PUBLIC_KEY.txt)
elif [ -f ~/.ssh/id_rsa_github_actions.pub ]; then
    PUB_KEY=$(cat ~/.ssh/id_rsa_github_actions.pub)
else
    echo -e "${YELLOW}⚠️  Публичный ключ не найден${NC}"
    PUB_KEY=""
fi

if [ -n "$PUB_KEY" ]; then
    if ssh -o ConnectTimeout=5 "$SERVER_USER@$SERVER_IP" "echo '$PUB_KEY' >> ~/.ssh/authorized_keys" 2>/dev/null; then
        echo -e "${GREEN}✅ SSH ключ добавлен на сервер${NC}"
    else
        echo -e "${YELLOW}⚠️  Добавьте ключ вручную:${NC}"
        echo -e "${BLUE}$PUB_KEY${NC}"
        echo -e "${BLUE}Добавьте в ~/.ssh/authorized_keys на сервере${NC}"
    fi
fi

echo -e "\n${GREEN}✅ Автоматическая настройка завершена!${NC}"
echo -e "\n${BLUE}📋 Проверьте:${NC}"
echo -e "  1. GitHub → Actions → должен быть workflow файл"
echo -e "  2. GitHub → Settings → Secrets → должны быть 4 секрета"
echo -e "  3. Сервер: $SERVER_USER@$SERVER_IP:$SERVER_PATH"
echo -e "\n${BLUE}🧪 Тест деплоя:${NC}"
echo -e "  git push origin main"

