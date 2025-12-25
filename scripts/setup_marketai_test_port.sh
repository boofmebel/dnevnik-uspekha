#!/bin/bash
# Скрипт для настройки тестового MarketAI на отдельном порту

SERVER="root@89.104.74.123"
TEST_PORT=9000  # Свободный порт для тестового MarketAI

echo "🔧 Настройка тестового MarketAI на порту $TEST_PORT..."

ssh $SERVER << 'EOF'
# Проверяем, есть ли уже конфигурация для тестового MarketAI
if [ -f /etc/nginx/sites-available/marketai-test ]; then
    echo "⚠️  Конфигурация для тестового MarketAI уже существует"
else
    echo "📝 Создаём конфигурацию для тестового MarketAI..."
    
    cat > /etc/nginx/sites-available/marketai-test << 'NGINX_CONFIG'
# Тестовый MarketAI
server {
    listen 9000;
    server_name 89.104.74.123;

    access_log /var/log/nginx/marketai-test_access.log;
    error_log /var/log/nginx/marketai-test_error.log;

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:5002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Увеличенные таймауты для долгих операций
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
        
        # Буферизация
        proxy_buffering off;
        proxy_request_buffering off;
    }
}
NGINX_CONFIG

    # Создаём симлинк
    ln -sf /etc/nginx/sites-available/marketai-test /etc/nginx/sites-enabled/marketai-test
    
    echo "✅ Конфигурация создана"
fi

# Проверяем конфигурацию
echo "🔍 Проверка конфигурации Nginx..."
nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Конфигурация корректна"
    echo "🔄 Перезагружаем Nginx..."
    systemctl reload nginx
    echo "✅ Nginx перезагружен"
else
    echo "❌ Ошибка в конфигурации Nginx"
    exit 1
fi

# Проверяем доступность порта
echo "🔍 Проверка доступности порта 9000..."
netstat -tlnp | grep :9000

echo ""
echo "✅ Готово!"
echo "📋 Тестовый MarketAI доступен на: http://89.104.74.123:9000"
EOF

echo ""
echo "✅ Настройка завершена!"
echo ""
echo "📋 Ссылки:"
echo "   MarketAI (продакшн): http://89.104.74.123"
echo "   MarketAI (тест):     http://89.104.74.123:9000"






