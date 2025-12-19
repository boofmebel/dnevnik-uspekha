# 📋 Анализ логики регистрации и сохранения в БД

## 🔍 Текущая архитектура

### Поток регистрации:
1. **Frontend** (`frontend/src/js/register.js`) → отправляет запрос
2. **Router** (`backend/routers/auth.py`) → `/register` endpoint
3. **Service** (`backend/services/auth_service.py`) → бизнес-логика
4. **Repository** (`backend/repositories/user_repository.py`) → доступ к БД
5. **Model** (`backend/models/user.py`) → SQLAlchemy модель

## ❌ Найденные проблемы

### 1. **КРИТИЧНО: Отсутствие коммита в репозитории**
**Проблема:** В `user_repository.py` метод `create()` использует только `flush()`, но не делает `commit()`.

```python
# backend/repositories/user_repository.py:38-44
async def create(self, user_data: dict) -> User:
    user = User(**user_data)
    self.session.add(user)
    await self.session.flush()  # ✅ Отправляет в БД, но не коммитит
    await self.session.refresh(user)
    return user
```

**Почему это проблема:**
- `flush()` отправляет SQL в БД, но не завершает транзакцию
- Коммит происходит в `get_db()` dependency, но только если нет исключений
- Если между `flush()` и `commit()` происходит ошибка, пользователь не сохранится
- При конкурентных запросах возможны race conditions

**Сравнение с другими репозиториями:**
Все репозитории используют одинаковый паттерн (`flush()` + `refresh()`), что означает, что проблема системная.

### 2. **Валидация email в двух местах**
**Проблема:** Email валидируется и в схеме, и в сервисе.

```python
# backend/schemas/auth.py:29
email: Optional[str] = None  # ❌ Не EmailStr, хотя должен быть

# backend/services/auth_service.py:35-39
if email and email.strip():
    import re
    email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    if not re.match(email_pattern, email.strip()):  # ❌ Дублирование валидации
        raise ValueError("Неверный формат email")
```

**Почему это проблема:**
- Дублирование логики
- В схеме используется `Optional[str]` вместо `Optional[EmailStr]`
- Валидация в сервисе менее надежна, чем Pydantic

### 3. **Отсутствие обработки IntegrityError**
**Проблема:** Нет обработки ошибок уникальности на уровне БД.

```python
# backend/services/auth_service.py:30-32
existing_user = await self.user_repo.get_by_phone(normalized_phone)
if existing_user:
    raise ValueError("Пользователь с таким номером телефона уже существует")
```

**Почему это проблема:**
- Race condition: два запроса могут одновременно проверить и создать пользователя
- Нет обработки `IntegrityError` от PostgreSQL
- При конкурентных запросах возможны дубликаты

### 4. **Нормализация роли в нескольких местах**
**Проблема:** Роль нормализуется в разных местах по-разному.

```python
# backend/services/auth_service.py:58-63
role = user.role
if hasattr(role, 'value'):
    role = role.value
elif not isinstance(role, str):
    role = str(role)
```

**Почему это проблема:**
- Дублирование логики
- В модели `role` объявлен как `String`, но может быть enum
- Несогласованность типов

### 5. **Отсутствие транзакционной целостности**
**Проблема:** Если создание пользователя успешно, но сохранение refresh token падает, пользователь остается без токена.

```python
# backend/routers/auth.py:108-119
user = await auth_service.register(...)
access_token = auth_service.create_access_token(...)
refresh_token = auth_service.create_refresh_token(...)
await auth_service.save_refresh_token(...)  # ❌ Если падает здесь, пользователь создан, но токен не сохранен
```

### 6. **Отсутствие валидации роли**
**Проблема:** Роль передается как строка без валидации.

```python
# backend/schemas/auth.py:28
role: str = "parent"  # ❌ Любая строка, не только валидные роли
```

## ✅ Рекомендации по исправлению

### 1. **Исправить валидацию email в схеме**
```python
# backend/schemas/auth.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class RegisterRequest(BaseModel):
    phone: str = Field(..., description="Номер телефона в формате +7XXXXXXXXXX")
    password: str = Field(..., min_length=8, description="Пароль минимум 8 символов")
    role: str = Field(default="parent", pattern="^(parent|admin|child)$")  # ✅ Валидация роли
    email: Optional[EmailStr] = None  # ✅ Использовать EmailStr
```

### 2. **Убрать дублирование валидации email**
```python
# backend/services/auth_service.py
async def register(self, phone: str, password: str, role: str = "parent", email: Optional[str] = None) -> dict:
    # Убрать валидацию email - она уже в схеме
    if email and email.strip():
        existing_email_user = await self.user_repo.get_by_email(email.strip())
        if existing_email_user:
            raise ValueError("Пользователь с таким email уже существует")
```

### 3. **Добавить обработку IntegrityError**
```python
# backend/services/auth_service.py
from sqlalchemy.exc import IntegrityError

async def register(self, phone: str, password: str, role: str = "parent", email: Optional[str] = None) -> dict:
    try:
        user = await self.user_repo.create(user_data)
    except IntegrityError as e:
        # Обработка дубликатов на уровне БД
        if "phone" in str(e.orig):
            raise ValueError("Пользователь с таким номером телефона уже существует")
        elif "email" in str(e.orig):
            raise ValueError("Пользователь с таким email уже существует")
        raise
```

### 4. **Использовать enum для роли**
```python
# backend/models/user.py
from models.user import UserRole

class User(Base):
    role = Column(Enum(UserRole), nullable=False)  # ✅ Использовать Enum

# backend/schemas/auth.py
from models.user import UserRole

class RegisterRequest(BaseModel):
    role: UserRole = UserRole.PARENT  # ✅ Использовать enum
```

### 5. **Добавить транзакционную целостность**
```python
# backend/routers/auth.py
from sqlalchemy.exc import IntegrityError

@router.post("/register")
async def register(request: RegisterRequest, response: Response, db: AsyncSession = Depends(get_db)):
    try:
        # Все операции в одной транзакции
        user = await auth_service.register(...)
        access_token = auth_service.create_access_token(...)
        refresh_token = auth_service.create_refresh_token(...)
        await auth_service.save_refresh_token(...)
        
        # Коммит только если все успешно
        await db.commit()
        
        return LoginResponse(...)
    except IntegrityError as e:
        await db.rollback()
        # Обработка ошибок
    except Exception as e:
        await db.rollback()
        raise
```

### 6. **Улучшить обработку ошибок в репозитории**
```python
# backend/repositories/user_repository.py
from sqlalchemy.exc import IntegrityError

async def create(self, user_data: dict) -> User:
    try:
        user = User(**user_data)
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user
    except IntegrityError as e:
        # Пробрасываем для обработки в сервисе
        raise
```

## 📊 Сравнение с best practices

### ✅ Что сделано правильно:
1. Разделение на слои (Router → Service → Repository)
2. Использование async/await
3. Валидация на уровне схем
4. Нормализация телефона
5. Хеширование паролей

### ❌ Что нужно исправить:
1. Транзакционная целостность
2. Обработка конкурентных запросов
3. Валидация роли
4. Удаление дублирования валидации
5. Обработка IntegrityError

## 🎯 Приоритет исправлений

1. **ВЫСОКИЙ:** Добавить обработку IntegrityError
2. **ВЫСОКИЙ:** Исправить валидацию email в схеме
3. **СРЕДНИЙ:** Использовать enum для роли
4. **СРЕДНИЙ:** Убрать дублирование валидации
5. **НИЗКИЙ:** Улучшить транзакционную целостность (если refresh token сохраняется в БД)

