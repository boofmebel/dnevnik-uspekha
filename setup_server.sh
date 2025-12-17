#!/bin/bash

# Скрипт для настройки сервера
# Использование: ./setup_server.sh

# ВАЖНО: Установите IP адрес сервера через переменную окружения
# export SERVER_IP=your-server-ip
# или отредактируйте эту строку:
SERVER_IP="${SERVER_IP:-YOUR_SERVER_IP_HERE}"
SERVER_USER="${1:-root}"
SERVER_PATH="/var/www/dnevnik-uspekha"

if [ "$SERVER_IP" = "YOUR_SERVER_IP_HERE" ]; then
    echo "❌ Ошибка: Установите SERVER_IP перед запуском"
    echo "export SERVER_IP=your-server-ip"
    exit 1
fi

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

