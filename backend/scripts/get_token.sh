#!/bin/bash
# Скрипт для получения токена через curl

echo "🔐 Получение токена..."
echo ""
echo "Введите данные для входа:"
read -p "Номер телефона (например, +79991234567): " PHONE
read -p "Пароль: " -s PASSWORD
echo ""

RESPONSE=$(curl -s -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"phone\": \"$PHONE\", \"password\": \"$PASSWORD\"}")

echo ""
echo "Ответ сервера:"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"

TOKEN=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)

if [ -n "$TOKEN" ]; then
  echo ""
  echo "✅ Токен получен:"
  echo "$TOKEN"
  echo ""
  echo "📋 Скопируйте этот токен выше"
else
  echo ""
  echo "❌ Не удалось получить токен. Проверьте данные для входа."
fi

