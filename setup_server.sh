#!/bin/bash

# Скрипт для настройки сервера
# Использование: ./setup_server.sh

SERVER_IP="89.104.74.123"
SERVER_USER="${1:-root}"
SERVER_PATH="/var/www/dnevnik-uspekha"

echo "🔧 Настройка сервера $SERVER_IP..."

echo ""
echo "📋 Выполните на сервере следующие команды:"
echo ""
echo "1. Подключитесь к серверу:"
echo "   ssh $SERVER_USER@$SERVER_IP"
echo ""
echo "2. Выполните на сервере:"
echo "   sudo mkdir -p $SERVER_PATH"
echo "   sudo chown -R \$USER:\$USER $SERVER_PATH"
echo "   cd $SERVER_PATH"
echo "   git clone https://github.com/boofmebel/dnevnik-uspekha.git ."
echo ""
echo "3. Добавьте публичный SSH ключ на сервер:"
echo "   (скопируйте содержимое SSH_PUBLIC_KEY.txt в ~/.ssh/authorized_keys на сервере)"
echo ""
echo "4. Проверьте доступ:"
echo "   ssh $SERVER_USER@$SERVER_IP 'cd $SERVER_PATH && pwd'"
echo ""

