#!/bin/bash

# Скрипт для автоматической настройки GitHub Secrets и деплоя
# Использование: ./scripts/setup_auto_deploy.sh

set -e

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

REPO="boofmebel/dnevnik-uspekha"
GITHUB_API="https://api.github.com"

echo -e "${BLUE}🚀 Настройка автоматического деплоя${NC}"
echo ""

# Проверка наличия необходимых инструментов
check_dependencies() {
    echo -e "${YELLOW}Проверка зависимостей...${NC}"
    
    # Проверка gh CLI
    if ! command -v gh &> /dev/null; then
        echo -e "${RED}❌ GitHub CLI (gh) не установлен${NC}"
        echo -e "${YELLOW}Установите: brew install gh (macOS) или https://cli.github.com${NC}"
        echo ""
        read -p "Продолжить с использованием GitHub API напрямую? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
        USE_GH_CLI=false
    else
        USE_GH_CLI=true
        echo -e "${GREEN}✅ GitHub CLI найден${NC}"
    fi
    
    # Проверка jq (для парсинга JSON)
    if ! command -v jq &> /dev/null; then
        echo -e "${YELLOW}⚠️  jq не установлен (нужен для парсинга JSON)${NC}"
        echo -e "${YELLOW}Установите: brew install jq${NC}"
        USE_JQ=false
    else
        USE_JQ=true
        echo -e "${GREEN}✅ jq найден${NC}"
    fi
    
    echo ""
}

# Аутентификация в GitHub
authenticate_github() {
    if [ "$USE_GH_CLI" = true ]; then
        echo -e "${YELLOW}Проверка аутентификации GitHub CLI...${NC}"
        if gh auth status &> /dev/null; then
            echo -e "${GREEN}✅ Уже аутентифицирован в GitHub CLI${NC}"
            GITHUB_TOKEN=$(gh auth token)
        else
            echo -e "${YELLOW}Требуется аутентификация в GitHub CLI${NC}"
            gh auth login
            GITHUB_TOKEN=$(gh auth token)
        fi
    else
        echo -e "${YELLOW}Введите GitHub Personal Access Token:${NC}"
        echo -e "${BLUE}Создайте токен: https://github.com/settings/tokens/new${NC}"
        echo -e "${BLUE}Нужны права: repo, admin:repo_hook${NC}"
        read -s GITHUB_TOKEN
        echo ""
    fi
    
    # Проверка токена
    if [ -z "$GITHUB_TOKEN" ]; then
        echo -e "${RED}❌ Токен не получен${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Аутентификация успешна${NC}"
    echo ""
}

# Создание SSH ключа
create_ssh_key() {
    SSH_KEY_PATH="$HOME/.ssh/id_ed25519_github_deploy"
    
    if [ -f "$SSH_KEY_PATH" ]; then
        echo -e "${YELLOW}SSH ключ уже существует: $SSH_KEY_PATH${NC}"
        read -p "Использовать существующий? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            read -p "Создать новый? (y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                SSH_KEY_PATH="$HOME/.ssh/id_ed25519_github_deploy_$(date +%s)"
            fi
        fi
    fi
    
    if [ ! -f "$SSH_KEY_PATH" ]; then
        echo -e "${YELLOW}Создание SSH ключа...${NC}"
        ssh-keygen -t ed25519 -C "github-actions-deploy-$(date +%s)" -f "$SSH_KEY_PATH" -N ""
        echo -e "${GREEN}✅ SSH ключ создан: $SSH_KEY_PATH${NC}"
    fi
    
    SSH_PRIVATE_KEY=$(cat "$SSH_KEY_PATH")
    SSH_PUBLIC_KEY=$(cat "${SSH_KEY_PATH}.pub")
    
    echo -e "${GREEN}✅ Публичный ключ:${NC}"
    echo "$SSH_PUBLIC_KEY"
    echo ""
    echo -e "${YELLOW}⚠️  Скопируйте публичный ключ выше и добавьте на сервер:${NC}"
    echo -e "${BLUE}ssh-copy-id -i ${SSH_KEY_PATH}.pub user@your-server.com${NC}"
    echo ""
    read -p "Нажмите Enter после добавления ключа на сервер..."
}

# Получение данных о сервере
get_server_info() {
    echo -e "${YELLOW}Введите данные о сервере:${NC}"
    echo ""
    
    read -p "SERVER_HOST (IP или домен): " SERVER_HOST
    read -p "SERVER_USER (пользователь SSH): " SERVER_USER
    read -p "SERVER_PATH (путь к проекту на сервере): " SERVER_PATH
    read -p "SERVER_PORT (SSH порт, по умолчанию 22): " SERVER_PORT
    
    SERVER_PORT=${SERVER_PORT:-22}
    
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
}

# Добавление секрета через GitHub API
add_secret() {
    local secret_name=$1
    local secret_value=$2
    
    echo -e "${YELLOW}Добавление секрета: $secret_name${NC}"
    
    # Получаем публичный ключ репозитория для шифрования
    if [ "$USE_JQ" = true ]; then
        REPO_KEY_ID=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
            "$GITHUB_API/repos/$REPO/actions/secrets/public-key" | jq -r '.key_id')
        REPO_KEY=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
            "$GITHUB_API/repos/$REPO/actions/secrets/public-key" | jq -r '.key')
    else
        # Без jq - используем Python для парсинга
        REPO_KEY_RESPONSE=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
            "$GITHUB_API/repos/$REPO/actions/secrets/public-key")
        REPO_KEY_ID=$(echo "$REPO_KEY_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['key_id'])")
        REPO_KEY=$(echo "$REPO_KEY_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['key'])")
    fi
    
    if [ -z "$REPO_KEY" ] || [ "$REPO_KEY" = "null" ]; then
        echo -e "${RED}❌ Не удалось получить публичный ключ репозитория${NC}"
        echo -e "${YELLOW}Проверьте права доступа токена${NC}"
        return 1
    fi
    
    # Шифруем секрет используя публичный ключ (требует Python с библиотекой PyNaCl)
    ENCRYPTED_VALUE=$(python3 <<EOF
import base64
from nacl import encoding, public

def encrypt(public_key: str, secret_value: str) -> str:
    """Шифрует секрет используя публичный ключ репозитория"""
    public_key_bytes = base64.b64decode(public_key)
    public_key_obj = public.PublicKey(public_key_bytes)
    sealed_box = public.SealedBox(public_key_obj)
    encrypted = sealed_box.encrypt(secret_value.encode('utf-8'))
    return base64.b64encode(encrypted).decode('utf-8')

print(encrypt("$REPO_KEY", """$secret_value"""))
EOF
)
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Ошибка шифрования. Установите PyNaCl: pip3 install pynacl${NC}"
        return 1
    fi
    
    # Отправляем зашифрованный секрет
    RESPONSE=$(curl -s -w "\n%{http_code}" -X PUT \
        -H "Authorization: token $GITHUB_TOKEN" \
        -H "Content-Type: application/json" \
        "$GITHUB_API/repos/$REPO/actions/secrets/$secret_name" \
        -d "{\"encrypted_value\":\"$ENCRYPTED_VALUE\",\"key_id\":\"$REPO_KEY_ID\"}")
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    
    if [ "$HTTP_CODE" = "204" ] || [ "$HTTP_CODE" = "201" ]; then
        echo -e "${GREEN}✅ Секрет $secret_name добавлен${NC}"
        return 0
    else
        echo -e "${RED}❌ Ошибка добавления секрета $secret_name (HTTP $HTTP_CODE)${NC}"
        echo "$RESPONSE" | head -n-1
        return 1
    fi
}

# Альтернативный метод через gh CLI
add_secret_gh_cli() {
    local secret_name=$1
    local secret_value=$2
    
    echo -e "${YELLOW}Добавление секрета через gh CLI: $secret_name${NC}"
    
    echo "$secret_value" | gh secret set "$secret_name" --repo "$REPO"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Секрет $secret_name добавлен${NC}"
        return 0
    else
        echo -e "${RED}❌ Ошибка добавления секрета $secret_name${NC}"
        return 1
    fi
}

# Основная функция
main() {
    check_dependencies
    authenticate_github
    create_ssh_key
    get_server_info
    
    echo ""
    echo -e "${BLUE}Добавление секретов в GitHub...${NC}"
    echo ""
    
    # Добавляем секреты
    if [ "$USE_GH_CLI" = true ]; then
        add_secret_gh_cli "SERVER_HOST" "$SERVER_HOST"
        add_secret_gh_cli "SERVER_USER" "$SERVER_USER"
        add_secret_gh_cli "SERVER_SSH_KEY" "$SSH_PRIVATE_KEY"
        add_secret_gh_cli "SERVER_PATH" "$SERVER_PATH"
        add_secret_gh_cli "SERVER_PORT" "$SERVER_PORT"
    else
        add_secret "SERVER_HOST" "$SERVER_HOST"
        add_secret "SERVER_USER" "$SERVER_USER"
        add_secret "SERVER_SSH_KEY" "$SSH_PRIVATE_KEY"
        add_secret "SERVER_PATH" "$SERVER_PATH"
        add_secret "SERVER_PORT" "$SERVER_PORT"
    fi
    
    echo ""
    echo -e "${GREEN}✅ Все секреты добавлены!${NC}"
    echo ""
    echo -e "${BLUE}📋 Следующие шаги:${NC}"
    echo "1. Убедитесь, что публичный SSH ключ добавлен на сервер:"
    echo "   ssh-copy-id -i ${SSH_KEY_PATH}.pub $SERVER_USER@$SERVER_HOST"
    echo ""
    echo "2. На сервере клонируйте репозиторий (если ещё не клонирован):"
    echo "   ssh $SERVER_USER@$SERVER_HOST"
    echo "   mkdir -p $SERVER_PATH"
    echo "   cd $SERVER_PATH"
    echo "   git clone https://github.com/$REPO.git ."
    echo ""
    echo "3. Сделайте push в main для тестирования деплоя:"
    echo "   git push origin main"
    echo ""
    echo "4. Проверьте деплой в GitHub Actions:"
    echo "   https://github.com/$REPO/actions"
    echo ""
    echo -e "${GREEN}🎉 Автоматический деплой настроен!${NC}"
}

# Запуск
main





