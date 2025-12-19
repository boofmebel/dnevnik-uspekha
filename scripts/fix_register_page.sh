#!/bin/bash

# Скрипт для исправления доступа к странице регистрации
# Добавляет правило в nginx для прямого доступа к register.html

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SERVER="root@89.104.74.123"

echo -e "${BLUE}🔧 Исправление доступа к странице регистрации${NC}"
echo ""

# Создаём резервную копию
echo -e "${YELLOW}Создание резервной копии...${NC}"
ssh "$SERVER" "cp /etc/nginx/sites-available/dnevnik-uspekha /etc/nginx/sites-available/dnevnik-uspekha.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || true"

# Обновляем конфигурацию nginx
echo -e "${YELLOW}Обновление конфигурации nginx...${NC}"
ssh "$SERVER" "cat > /tmp/nginx-update.sh <<'UPDATE_SCRIPT'
#!/bin/bash
CONFIG_FILE=\"/etc/nginx/sites-available/dnevnik-uspekha\"

# Читаем текущую конфигурацию
CONFIG=\$(cat \"\$CONFIG_FILE\")

# Проверяем, есть ли уже правило для register.html
if echo \"\$CONFIG\" | grep -q \"register.*\.html\"; then
    echo \"✅ Правило для register.html уже существует\"
    exit 0
fi

# Добавляем правило перед location /
# Заменяем первое вхождение \"location / { try_files\" на наше правило + location /
NEW_CONFIG=\$(echo \"\$CONFIG\" | sed 's|location / {|# Специальные HTML файлы отдаются напрямую (не через SPA роутинг)\n    location ~ ^/(register|admin|setup_token|install_token|setup_token_chrome)\\.html\\$ {\n        try_files \\$uri =404;\n    }\n    \n    # Основная локация (SPA роутинг для остальных запросов)\n    location / {|' | sed 's|try_files \\\\\$uri \\\\\$uri/ /index.html;|try_files \\\\\$uri \\\\\$uri/ /index.html;|')

# Записываем обновлённую конфигурацию
echo \"\$NEW_CONFIG\" > \"\$CONFIG_FILE\"
echo \"✅ Конфигурация обновлена\"
UPDATE_SCRIPT
chmod +x /tmp/nginx-update.sh
sudo /tmp/nginx-update.sh
"

# Проверка конфигурации
echo -e "${YELLOW}Проверка конфигурации nginx...${NC}"
if ssh "$SERVER" "sudo nginx -t" 2>&1 | grep -q "successful"; then
    echo -e "${GREEN}✅ Конфигурация корректна${NC}"
else
    echo -e "${RED}❌ Ошибка в конфигурации${NC}"
    ssh "$SERVER" "sudo nginx -t"
    exit 1
fi

# Перезагрузка nginx
echo -e "${YELLOW}Перезагрузка nginx...${NC}"
ssh "$SERVER" "sudo systemctl reload nginx"

echo ""
echo -e "${GREEN}✅ Конфигурация обновлена!${NC}"
echo ""
echo -e "${BLUE}🔗 Страница регистрации теперь доступна:${NC}"
echo "   http://89.104.74.123:3000/register.html"
echo ""
echo -e "${BLUE}📋 Также доступны:${NC}"
echo "   - http://89.104.74.123:3000/admin.html"
echo "   - http://89.104.74.123:3000/setup_token.html"
echo "   - http://89.104.74.123:3000/install_token.html"
echo ""

