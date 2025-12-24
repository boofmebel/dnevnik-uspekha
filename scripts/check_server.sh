#!/bin/bash
# Скрипт для проверки сервера через SSH

SERVER_HOST="${SERVER_HOST:-89.104.74.123}"
SERVER_USER="${SERVER_USER:-root}"
SERVER_PATH="${SERVER_PATH:-/var/www/dnevnik-uspekha}"

echo "🔍 Проверка сервера..."
echo ""

# Проверка существования frontend директории
echo "1️⃣ Проверка директории frontend:"
ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_HOST} "ls -la ${SERVER_PATH}/frontend/ | head -10" || echo "❌ Не удалось подключиться"

echo ""
echo "2️⃣ Проверка index.html:"
ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_HOST} "ls -la ${SERVER_PATH}/frontend/index.html" || echo "❌ index.html не найден"

echo ""
echo "3️⃣ Проверка конфигурации nginx:"
ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_HOST} "cat /etc/nginx/sites-available/dnevnik-uspekha | grep -A5 'listen 3000'" || echo "❌ Конфигурация не найдена"

echo ""
echo "4️⃣ Проверка прав доступа:"
ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_HOST} "stat -c '%U:%G %a' ${SERVER_PATH}/frontend 2>/dev/null || stat -f '%Su:%Sg %OLp' ${SERVER_PATH}/frontend"

echo ""
echo "5️⃣ Проверка логов nginx:"
ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_HOST} "tail -5 /var/log/nginx/dnevnik-uspekha-error.log 2>/dev/null || tail -5 /var/log/nginx/error.log"

