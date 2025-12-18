#!/bin/bash

# Автоматическая настройка проекта для GitHub и деплоя

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Автоматическая настройка проекта${NC}\n"

# 1. Настройка Git
echo -e "${YELLOW}📝 Настройка Git...${NC}"
if ! git config --global user.name > /dev/null 2>&1; then
    git config --global user.name "Evgeniy Pomytkin"
    echo -e "${GREEN}✅ Git user.name настроен${NC}"
fi

if ! git config --global user.email > /dev/null 2>&1; then
    git config --global user.email "evgeniypomytkin@users.noreply.github.com"
    echo -e "${GREEN}✅ Git user.email настроен${NC}"
fi

# 2. Проверка SSH ключа
echo -e "\n${YELLOW}🔑 Проверка SSH ключа...${NC}"
SSH_KEY_PATH="$HOME/.ssh/id_rsa_github_actions"
if [ -f "$SSH_KEY_PATH" ]; then
    echo -e "${GREEN}✅ SSH ключ найден: $SSH_KEY_PATH${NC}"
    echo -e "${BLUE}📋 Публичный ключ (добавьте на сервер):${NC}"
    cat "${SSH_KEY_PATH}.pub"
    echo ""
    echo -e "${BLUE}📋 Приватный ключ (для GitHub Secrets SERVER_SSH_KEY):${NC}"
    cat "$SSH_KEY_PATH"
    echo ""
else
    echo -e "${YELLOW}⚠️  SSH ключ не найден, создаю новый...${NC}"
    ssh-keygen -t ed25519 -f "$HOME/.ssh/id_ed25519_deploy" -N "" -C "github-actions-deploy"
    SSH_KEY_PATH="$HOME/.ssh/id_ed25519_deploy"
    echo -e "${GREEN}✅ Новый SSH ключ создан: $SSH_KEY_PATH${NC}"
    echo -e "${BLUE}📋 Публичный ключ (добавьте на сервер):${NC}"
    cat "${SSH_KEY_PATH}.pub"
    echo ""
    echo -e "${BLUE}📋 Приватный ключ (для GitHub Secrets SERVER_SSH_KEY):${NC}"
    cat "$SSH_KEY_PATH"
    echo ""
fi

# 3. Проверка текущего состояния
echo -e "\n${YELLOW}📊 Текущее состояние репозитория:${NC}"
echo -e "Ветка: $(git branch --show-current)"
echo -e "Коммитов: $(git rev-list --count HEAD)"
echo -e "Файлов: $(git ls-files | wc -l)"

# 4. Проверка remote
echo -e "\n${YELLOW}🔗 Проверка подключения к GitHub...${NC}"
if git remote get-url origin > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Remote настроен:${NC}"
    git remote -v
else
    echo -e "${YELLOW}⚠️  Remote не настроен${NC}"
    echo -e "${BLUE}После создания репозитория на GitHub выполните:${NC}"
    echo -e "  git remote add origin https://github.com/ВАШ_USERNAME/НАЗВАНИЕ_РЕПОЗИТОРИЯ.git"
fi

# 5. Создание файла с инструкциями
echo -e "\n${YELLOW}📝 Создание файла с инструкциями...${NC}"
cat > GITHUB_SETUP_STEPS.md << 'EOF'
# Шаги для завершения настройки

## ✅ Уже выполнено автоматически:
- ✅ Git user.name и user.email настроены
- ✅ SSH ключ подготовлен
- ✅ Workflow файл создан

## 📋 Что нужно сделать вручную:

### 1. Создайте репозиторий на GitHub
1. Перейдите на https://github.com/new
2. Название: `dnevnik-uspekha` (или другое)
3. Выберите: **Private** или **Public**
4. **НЕ** добавляйте README, .gitignore или license (они уже есть)
5. Нажмите "Create repository"

### 2. Подключите локальный репозиторий
```bash
git remote add origin https://github.com/ВАШ_USERNAME/dnevnik-uspekha.git
git push -u origin main
git checkout dev
git push -u origin dev
git checkout main
```

### 3. Настройте Secrets в GitHub
1. Перейдите: Settings → Secrets and variables → Actions
2. Добавьте секреты:

**SERVER_HOST:**
```
ваш-сервер.com
или
192.168.1.100
```

**SERVER_USER:**
```
root
или
deploy
```

**SERVER_SSH_KEY:**
```
[скопируйте приватный ключ из вывода скрипта выше]
```

**SERVER_PATH:**
```
/var/www/dnevnik-uspekha
```

### 4. Подготовьте сервер
```bash
# Подключитесь к серверу
ssh user@your-server.com

# Создайте директорию
sudo mkdir -p /var/www/dnevnik-uspekha
sudo chown -R $USER:$USER /var/www/dnevnik-uspekha

# Клонируйте репозиторий
cd /var/www/dnevnik-uspekha
git clone https://github.com/ВАШ_USERNAME/dnevnik-uspekha.git .

# Или если репозиторий уже есть:
git init
git remote add origin https://github.com/ВАШ_USERNAME/dnevnik-uspekha.git
```

### 5. Добавьте SSH ключ на сервер
```bash
# Скопируйте публичный ключ на сервер
ssh-copy-id -i ~/.ssh/id_rsa_github_actions.pub user@your-server.com

# Или вручную добавьте в ~/.ssh/authorized_keys на сервере
```

### 6. Проверьте деплой
```bash
# Сделайте небольшое изменение
echo "# Test" >> README.md
git add .
git commit -m "Test deployment"
git push origin main
```

Затем проверьте: GitHub → Actions → должен быть успешный деплой ✅

EOF

echo -e "${GREEN}✅ Файл GITHUB_SETUP_STEPS.md создан${NC}"

echo -e "\n${GREEN}✅ Автоматическая настройка завершена!${NC}"
echo -e "${BLUE}📖 Смотрите GITHUB_SETUP_STEPS.md для следующих шагов${NC}"

