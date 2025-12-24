"""
Тестовый скрипт для проверки создания ребенка через API (имитация frontend запроса)
"""
import asyncio
import sys
from pathlib import Path

backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from schemas.child import ChildCreate
from models.child import Gender

async def test_api_create():
    """Тест создания ребенка через Pydantic схему (как от frontend)"""
    print("🧪 Тестирование создания ребенка через API (Pydantic схему)...")
    
    try:
        # Имитируем данные от frontend (строка для gender)
        data_from_frontend = {
            "name": "Тест API",
            "gender": "girl",  # Строка, как от frontend
            "avatar": None
        }
        
        print(f"📤 Данные от frontend: {data_from_frontend}")
        
        # Создаем Pydantic модель (как в роутере)
        child_data = ChildCreate(**data_from_frontend)
        print(f"✅ Pydantic модель создана: {child_data}")
        print(f"   gender тип: {type(child_data.gender)}, значение: {child_data.gender}")
        
        # Имитируем model_dump (как в роутере)
        child_dict = child_data.model_dump(exclude_unset=True, mode='python')
        print(f"📋 После model_dump(mode='python'): {child_dict}")
        print(f"   gender тип: {type(child_dict.get('gender'))}, значение: {child_dict.get('gender')}")
        
        # Проверяем конвертацию
        from models.child import Gender
        if 'gender' in child_dict:
            gender_value = child_dict['gender']
            if isinstance(gender_value, Gender):
                child_dict['gender'] = gender_value.value
                print(f"✅ Конвертирован Gender enum в строку: {gender_value.value}")
            elif isinstance(gender_value, str):
                print(f"✅ Gender уже строка: {gender_value}")
            else:
                print(f"⚠️ Неожиданный тип gender: {type(gender_value)}")
        
        print(f"📋 Финальные данные: {child_dict}")
        print("✅ Тест пройден успешно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_api_create())
    sys.exit(0 if success else 1)

