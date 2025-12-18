#!/bin/bash
# Скрипт для деплоя админки на сервер

SERVER="root@89.104.74.123"
SERVER_PATH="/var/www/dnevnik-uspekha"
LOCAL_PATH="frontend"

echo "🚀 Деплой админки на сервер..."

# Создаём директории если их нет
ssh $SERVER "cd $SERVER_PATH && mkdir -p src/js static/css"

# Копируем файлы админки
echo "📦 Копирование файлов..."
scp $LOCAL_PATH/admin.html $SERVER:$SERVER_PATH/admin.html
scp $LOCAL_PATH/src/js/admin.js $SERVER:$SERVER_PATH/src/js/admin.js
scp $LOCAL_PATH/static/css/admin.css $SERVER:$SERVER_PATH/static/css/admin.css

# Копируем зависимости если их нет
echo "📦 Копирование зависимостей..."
scp $LOCAL_PATH/src/js/error-handler.js $SERVER:$SERVER_PATH/src/js/error-handler.js
scp $LOCAL_PATH/src/js/utils.js $SERVER:$SERVER_PATH/src/js/utils.js
scp $LOCAL_PATH/src/js/api.js $SERVER:$SERVER_PATH/src/js/api.js

# Проверяем
echo "🔍 Проверка..."
ssh $SERVER "cd $SERVER_PATH && \
  test -f admin.html && echo '✅ admin.html' || echo '❌ admin.html' && \
  test -f src/js/admin.js && echo '✅ admin.js' || echo '❌ admin.js' && \
  test -f static/css/admin.css && echo '✅ admin.css' || echo '❌ admin.css' && \
  test -f src/js/api.js && echo '✅ api.js' || echo '❌ api.js'"

echo ""
echo "✅ Деплой завершён!"
echo "🔗 Админка доступна: http://89.104.74.123:3000/admin.html"

