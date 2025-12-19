#!/usr/bin/env python3
"""
Скрипт для прямой генерации токена (без БД)
"""
import sys
from pathlib import Path

backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from core.config import settings
from core.security.jwt import create_access_token
from datetime import timedelta

def main():
    print("=" * 60)
    print("🔐 Генерация токена напрямую")
    print("=" * 60)
    
    # Проверяем SECRET_KEY
    if not settings.SECRET_KEY:
        print("❌ SECRET_KEY не установлен!")
        return 1
    
    print(f"✅ SECRET_KEY найден (длина: {len(settings.SECRET_KEY)})")
    
    # Создаем токен для тестового администратора
    # user_id = 1 (предполагаем, что это администратор)
    user_id = 1
    role = "admin"
    
    print(f"\n🎫 Создание токена для:")
    print(f"   User ID: {user_id}")
    print(f"   Role: {role}")
    
    # Создаем токен с увеличенным временем жизни для тестирования
    token_data = {
        "sub": str(user_id),
        "role": role
    }
    
    # Токен на 24 часа для тестирования
    token = create_access_token(token_data, expires_delta=timedelta(hours=24))
    
    print("\n" + "=" * 60)
    print("✅ ТОКЕН СОЗДАН:")
    print("=" * 60)
    print(token)
    print("=" * 60)
    
    # Проверяем токен
    print("\n🔍 Проверка токена...")
    from core.security.jwt import verify_token
    
    payload = verify_token(token)
    if payload:
        print("✅ Токен валиден!")
        print(f"   User ID: {payload.get('sub')}")
        print(f"   Role: {payload.get('role')}")
        print(f"   Type: {payload.get('type')}")
        print(f"   Exp: {payload.get('exp')}")
        
        print("\n" + "=" * 60)
        print("📋 ИНСТРУКЦИЯ:")
        print("=" * 60)
        print("1. Скопируйте токен выше")
        print("2. Откройте консоль браузера (F12)")
        print("3. Выполните:")
        print(f"   localStorage.setItem('admin_token', '{token}');")
        print("4. Обновите страницу админки")
        print("=" * 60)
        
        return 0
    else:
        print("❌ Токен невалиден!")
        return 1

if __name__ == "__main__":
    sys.exit(main())

