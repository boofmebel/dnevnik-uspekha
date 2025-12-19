#!/usr/bin/env python3
"""
Скрипт для тестирования основных endpoints
"""
import requests
import json
import sys
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def test_endpoint(method: str, endpoint: str, data: Dict = None, headers: Dict = None) -> Dict[str, Any]:
    """Тестирование endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=5)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers, timeout=5)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=5)
        else:
            return {"error": f"Неизвестный метод: {method}"}
        
        return {
            "status_code": response.status_code,
            "success": 200 <= response.status_code < 300,
            "data": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text[:200]
        }
    except requests.exceptions.ConnectionError:
        return {"error": "Не удалось подключиться к серверу. Убедитесь, что сервер запущен."}
    except Exception as e:
        return {"error": str(e)}

def main():
    """Основная функция тестирования"""
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ ENDPOINTS")
    print("=" * 60)
    
    # Тест 1: Health check
    print("\n1. Тест /health")
    result = test_endpoint("GET", "/health")
    if "error" in result:
        print(f"   ❌ Ошибка: {result['error']}")
    elif result["success"]:
        print(f"   ✅ Статус: {result['status_code']}")
        print(f"   📄 Ответ: {json.dumps(result['data'], indent=2, ensure_ascii=False)}")
    else:
        print(f"   ❌ Статус: {result['status_code']}")
    
    # Тест 2: Ready check
    print("\n2. Тест /ready")
    result = test_endpoint("GET", "/ready")
    if "error" in result:
        print(f"   ❌ Ошибка: {result['error']}")
    elif result["success"]:
        print(f"   ✅ Статус: {result['status_code']}")
        print(f"   📄 Ответ: {json.dumps(result['data'], indent=2, ensure_ascii=False)}")
    else:
        print(f"   ❌ Статус: {result['status_code']}")
        print(f"   📄 Ответ: {result.get('data', 'Нет данных')}")
    
    # Тест 3: Root endpoint
    print("\n3. Тест /")
    result = test_endpoint("GET", "/")
    if "error" in result:
        print(f"   ❌ Ошибка: {result['error']}")
    elif result["success"]:
        print(f"   ✅ Статус: {result['status_code']}")
        print(f"   📄 Ответ: {json.dumps(result['data'], indent=2, ensure_ascii=False)}")
    else:
        print(f"   ❌ Статус: {result['status_code']}")
    
    # Тест 4: API root
    print("\n4. Тест /api/")
    result = test_endpoint("GET", "/api/")
    if "error" in result:
        print(f"   ❌ Ошибка: {result['error']}")
    elif result["success"]:
        print(f"   ✅ Статус: {result['status_code']}")
    else:
        print(f"   ⚠️  Статус: {result['status_code']} (может быть нормально, если endpoint не существует)")
    
    # Тест 5: Register endpoint (без данных - должна быть ошибка валидации)
    print("\n5. Тест /api/auth/register (валидация)")
    result = test_endpoint("POST", "/api/auth/register", {})
    if "error" in result:
        print(f"   ❌ Ошибка: {result['error']}")
    elif result["status_code"] == 422:
        print(f"   ✅ Валидация работает (ожидаемая ошибка 422)")
    else:
        print(f"   ⚠️  Статус: {result['status_code']}")
    
    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 60)
    
    print("\n💡 Для полного тестирования:")
    print("   1. Запустите сервер: cd backend && uvicorn main:app --reload")
    print("   2. Запустите этот скрипт: python scripts/test_endpoints.py")
    print("   3. Протестируйте авторизацию через браузер или Postman")

if __name__ == "__main__":
    main()

